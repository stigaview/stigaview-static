import datetime
import os.path
import pathlib
import re
import xml.etree.ElementTree as ET

from stigaview_static import models

NS = {
    "xccdf-1.2": "http://checklists.nist.gov/xccdf/1.2",
    "xccdf-1.1": "http://checklists.nist.gov/xccdf/1.1",
}


def _disa_text_to_html(text: str) -> str:
    return text.replace("\n", "<br />")


def _get_description_root(stig_xml):
    description = "<root>"
    description += (
        stig_xml.find("xccdf-1.1:description", NS)
        .text.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&", "&amp;")
    )
    description += "</root>"
    description_root = ET.ElementTree(ET.fromstring(description)).getroot()
    return description_root


def import_stig(stig_path: pathlib.Path, release_date: datetime.date) -> models.Stig:
    root = _get_root_from_xml_path(stig_path)
    release, version = _get_stig_verison(str(stig_path.absolute()))
    stig = models.Stig(version=version, release=release, release_date=release_date)
    for group in root.findall("xccdf-1.1:Group", NS):
        for stig_xml in group.findall("xccdf-1.1:Rule", NS):
            srg = group.find("xccdf-1.1:title", NS).text
            title = stig_xml.find("xccdf-1.1:title", NS).text
            description_root = _get_description_root(stig_xml)
            cci_from_source = stig_xml.find(
                "xccdf-1.1:ident[@system='http://cyber.mil/cci']", NS
            ).text
            control = models.Control()
            control.severity = stig_xml.attrib["severity"]
            control.srg = srg
            control.id = stig_xml.find("xccdf-1.1:version", NS).text
            control.disa_stig_id = control.id
            control.description = _disa_text_to_html(
                description_root.find("VulnDiscussion").text
            )
            control.fix = _disa_text_to_html(
                stig_xml.find("xccdf-1.1:fixtext", NS).text
            )
            control.check = _disa_text_to_html(
                stig_xml.find("xccdf-1.1:check/xccdf-1.1:check-content", NS).text
            )
            control.cci = cci_from_source
            control.title = title
            stig.controls.append(control)
    return stig


def _get_stig_verison(stig_path):
    base_name = os.path.basename(stig_path)
    matcher = r"^v(\d+)r(\d+).xml$"
    matches = re.match(matcher, base_name)
    if not matches:
        raise ValueError(f"Stig at {stig_path} cannot be version matched.")
    version = matches.group(1)
    release = matches.group(2)
    return release, version


def _get_root_from_xml_path(stig_path) -> ET.ElementTree:
    with open(stig_path) as stig_file:
        root = ET.ElementTree(ET.fromstring(stig_file.read()))
    return root
