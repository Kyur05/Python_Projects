import xml.etree.ElementTree as ET
def explore_landxml(file_name):
    print(f"Cracking open{file_name} ")
    try:
        tree = ET.parse(file_name)
        root = tree.getroot()
        ns = {'lx': root.tag.split('}')[0].strip('{')}
        alignments = root.findall('.//lx:Alignment', ns)
        print(f"\nFound {len(alignments)} Alignments(s)!")
        for align in alignments:
            align_name = align.get('name')
            print(f"\nAlignment: {align_name}")
            profiles = align.findall('.//lx:Profile', ns)
            for prof in profiles:
                prof_name = prof.get('name')
                print(f" Associated Profile: {prof_name} ")
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find '{file_name}'.")
explore_landxml("road_export.xml")