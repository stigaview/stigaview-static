#!/usr/bin/env python3

import argparse
import glob
import pathlib
import re
import sys
import zipfile


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-root", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--release-date", required=True)
    return parser.parse_args()


disa_to_shortname = {
    "RHEL_8": "rhel8",
    "RHEL_9": "rhel9",
    "Apple_iOS-iPadOS_18": "ios18",
    "Apple_macOS_13": "macos13",
    "Apple_macOS_14": "macos14",
    "Apple_macOS_15": "macos15",
    "CAN_Ubuntu_20-04_LTS": "ubuntu2004",
    "CAN_Ubuntu_22-04_LTS": "ubuntu2204",
    "CAN_Ubuntu_24-04_LTS": "ubuntu2404",
    "CL_AlmaLinux_OS_9": "alma9",
    "MS_Windows_10": "win10",
    "MS_Windows_11": "win11",
    "Oracle_Linux_7": "ol7",
    "Oracle_Linux_8": "ol8",
    "Oracle_Linux_9": "ol9",
    "SLES_15": "sle15",
    "SLES_12": "sle12",
    "MS_Windows_Server_2016": "winserv2016",
    "MS_Windows_Server_2019": "winserv2019",
    "MS_Windows_Server_2022": "winserv2022",
    "Container_Platform": "srg-ctr",
    "Mainframe_Product": "srg-mainframe",
    "RH_OpenShift_Container_Platform_4-12": "ocp",
    "RH_OpenShift_Container_Platform_4-x": "ocp",
    "GPOS": "srg-gpos",
    "Kubernetes": "srg-kubernetes",
    "TOSS_4": "toss4",
    "API": "srg-api",
    "RGS_RKE2": "rke2",
    "Amazon_Linux_2023": "al2023",
}


def main() -> int:
    print("starting")
    args = _parse_args()
    download_root = pathlib.Path(args.download_root)
    root = pathlib.Path(args.root)
    zip_files = glob.glob("*.zip", root_dir=download_root)
    for current_zip in zip_files:
        full_zip_path = download_root / current_zip
        with zipfile.ZipFile(full_zip_path, "r") as z:
            product_regex = r"U_(?P<product>.+)_V(?P<version>\d+)R(?P<release>\d+)_(?P<type>STIG|SRG)\.zip"
            product_regex_matches = re.match(product_regex, current_zip)
            if not product_regex_matches:
                print(
                    f"skipping {full_zip_path} since the file name doesn't match the normal pattern"
                )
                continue
            matches_dict = product_regex_matches.groupdict()
            version = matches_dict["version"]
            release = matches_dict["release"]
            product = matches_dict["product"]
            short_version = f"v{version}r{release}"
            if product not in disa_to_shortname:
                print(f"skipping {product} as it is not in known products")
                continue
            short_name = disa_to_shortname[product]
            for file_info in z.infolist():
                if file_info.filename.endswith(".xml"):
                    with z.open(file_info) as file:
                        filename = f"{short_version}.xml"
                        output_path = root / "products" / short_name / filename
                        if not output_path.exists():
                            xml_content = file.read().decode("utf-8")
                            output_path.write_text(xml_content)
                        else:
                            print(
                                f"File {str(output_path)} already exists for {short_name}.",
                                file=sys.stderr,
                            )
                        product_toml_path = (
                            root / "products" / short_name / "product.toml"
                        )
                        if short_version in product_toml_path.read_text():
                            continue
                        with open(product_toml_path, "a") as f:
                            f.write(f"[stigs.{short_version}]\n")
                            f.write(f"release_date = {args.release_date}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
