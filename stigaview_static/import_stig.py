import datetime
import html
import os.path
import pathlib
import re
import xml.etree.ElementTree as ET

from stigaview_static import models, utils

NS = {
    "xccdf-1.2": "http://checklists.nist.gov/xccdf/1.2",
    "xccdf-1.1": "http://checklists.nist.gov/xccdf/1.1",
}

KNOWN_DESCRIPTION_ELEMENTS = {
    "VulnDiscussion",
    "FalsePositives",
    "FalseNegatives",
    "Documentable",
    "Mitigations",
    "SeverityOverrideGuidance",
    "PotentialImpacts",
    "ThirdPartyTools",
    "MitigationControl",
    "Responsibility",
    "IAControls",
}


def _disa_text_to_html(text: str) -> str:
    return html.escape(text, True).replace("\n", "<br />")


def _escape_placeholders(text: str) -> str:
    def replacer(match):
        tag = match.group(1)
        if tag in KNOWN_DESCRIPTION_ELEMENTS:
            return match.group(0)
        return f"&lt;{tag}&gt;"

    return re.sub(r"<([a-zA-Z0-9_-]+)>", replacer, text)


def _get_description_root(stig_xml: ET.Element) -> dict:
    raw_description = stig_xml.find("xccdf-1.1:description", NS).text
    part_escaped = (
        _escape_placeholders(raw_description)
        .replace("<<<", "&lt;&lt;&lt;")
        .replace("&", "&amp;")
    )
    description = f"<root>{part_escaped}</root>"
    description_root = ET.ElementTree(ET.fromstring(description)).getroot()
    return description_root


def import_stig(
    stig_path: pathlib.Path, release_date: datetime.date, product: models.Product
) -> tuple[models.Stig, dict]:
    root = _get_root_from_xml_path(stig_path)
    release, version = _get_stig_version(str(stig_path.absolute()))
    stig = models.Stig(
        version=version, release=release, release_date=release_date, product=product
    )
    srgs = dict()
    for group in root.findall("xccdf-1.1:Group", NS):
        for stig_xml in group.findall("xccdf-1.1:Rule", NS):
            srg_id = group.find("xccdf-1.1:title", NS).text
            title = stig_xml.find("xccdf-1.1:title", NS).text
            description_root = _get_description_root(stig_xml)
            cci_from_source = stig_xml.findall(
                "xccdf-1.1:ident[@system='http://cyber.mil/cci']", NS
            )
            ccis = list()
            for cci in cci_from_source:
                ccis.append(cci.text)
            stig = stig
            severity = stig_xml.attrib["severity"]
            srg = models.Srg(srg_id=srg_id)
            disa_stig_id = stig_xml.find("xccdf-1.1:version", NS).text
            description = _disa_text_to_html(
                description_root.find("VulnDiscussion").text
            )
            fix = _disa_text_to_html(stig_xml.find("xccdf-1.1:fixtext", NS).text)
            check = _disa_text_to_html(
                stig_xml.find("xccdf-1.1:check/xccdf-1.1:check-content", NS).text
            )
            vulnerability_id = group.attrib["id"].replace("V-", "")
            control = models.Control(
                stig=stig,
                severity=severity,
                srg=srg,
                disa_stig_id=disa_stig_id,
                description=description,
                fix=fix,
                check=check,
                cci=ccis,
                title=title,
                vulnerability_id=vulnerability_id,
            )
            utils.update_dict_list(srgs, srg_id, control)
            stig.controls.append(control)
    return stig, srgs


def _get_stig_version(stig_path):
    base_name = os.path.basename(stig_path)
    matcher = r"^v(?P<version>\d+)r(?P<release>\d+).xml$"
    matches = re.match(matcher, base_name)
    if not matches:
        raise ValueError(f"Stig at {stig_path} cannot be version matched.")
    groups = matches.groupdict()
    version = groups["version"]
    release = groups["release"]
    return release, version


def _get_root_from_xml_path(stig_path) -> ET.ElementTree:
    with open(stig_path, encoding="utf-8") as stig_file:
        root = ET.ElementTree(ET.fromstring(stig_file.read()))
    return root
