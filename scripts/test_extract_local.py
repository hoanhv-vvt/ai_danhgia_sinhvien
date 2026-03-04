import asyncio
import json
import time
import os
from gemini_client import load_image, extract_student_info

def main(images):
    # Danh sách ảnh muốn test
    # images = [
    #     "SV/sv_13_1.jpeg",
    #     "SV/sv_13_2.jpeg",
    #     # "SV/sv_16_3.jpeg",
    #     # Thêm các ảnh khác vào đây
    # ],

    output_filename = "_".join(images[0].split("/")[-1].split("_")[:2]) + ".json"
    print(">> output_filename:", output_filename)
    if os.path.exists(output_filename):
        print(">> Output filename ALREADY EXISTS: ", output_filename)
        return

    loaded_images = []
    for source in images:
        try:
            print(f"Loading image: {source}")
            image_bytes, mime_type = load_image(source)
            loaded_images.append((image_bytes, mime_type))
        except Exception as e:
            print(f"Failed to load {source}: {e}")

    if not loaded_images:
        print("Không tải được ảnh nào.")
        return

    try:
        print(f"Đang gửi {len(loaded_images)} ảnh tới Gemini...")
        # Gọi thẳng function trong gemini_client, không qua API
        student_info = extract_student_info(loaded_images)
        print("\n--- KẾT QUẢ TRÍCH XUẤT ---")
        print(json.dumps(student_info.model_dump(), indent=2, ensure_ascii=False))
        with open(output_filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(student_info.model_dump(), indent=2, ensure_ascii=False))
            f.write("\n")
            
    except Exception as e:
        print(f"\n❌ Lỗi khi trích xuất: {e}")

    time.sleep(60)

if __name__ == "__main__":
    images_groups = [
        ["SV_cloud/result/case1_group1_689ace07bc6eb25325b71cce.jpeg",
        "SV_cloud/result/case1_group1_689ace1759bb23aae1ab3587.jpeg",],

        ["SV_cloud/result/case1_group2_689ad408892992d6ea1143f3.jpeg",],

        ["SV_cloud/result/case1_group3_689ad778892992d6ea1143fa.jpeg",],

        ["SV_cloud/result/case1_group4_689ae41959bb23aae1ab35a5.jpeg",],

        ["SV_cloud/result/case1_group5_689af23b7a433b7206d5758a.jpeg",
        "SV_cloud/result/case1_group5_689af23e59bb23aae1ab35c4.jpeg",
        "SV_cloud/result/case1_group5_689af2447a433b7206d5758c.jpeg",
        "SV_cloud/result/case1_group5_689af248892992d6ea114427.jpeg",],

        ["SV_cloud/result/case1_group6_689affd1bc6eb25325b71d0e.jpeg",],

        ["SV_cloud/result/case1_group7_689b03a9bc6eb25325b71d15.jpeg",
        "SV_cloud/result/case1_group7_689b039c892992d6ea11443e.jpeg",
        "SV_cloud/result/case1_group7_689b039d892992d6ea11443f.jpeg",
        "SV_cloud/result/case1_group7_689b039dbc6eb25325b71d14.jpeg",
        "SV_cloud/result/case1_group7_689b039e7a433b7206d575aa.jpeg",],

        ["SV_cloud/result/case1_group8_689b04f6bc6eb25325b71d18.jpeg",],

        ["SV_cloud/result/case1_group9_689b08bdbc6eb25325b71d1f.jpeg",
        "SV_cloud/result/case1_group9_689b08bebc6eb25325b71d20.jpeg",
        "SV_cloud/result/case1_group9_689b08bf59bb23aae1ab35e8.jpeg",
        "SV_cloud/result/case1_group9_689b08c87a433b7206d575b6.jpeg",
        "SV_cloud/result/case1_group9_689b08c159bb23aae1ab35e9.jpeg",],

        ["SV_cloud/result/case1_group10_689b0c6e892992d6ea11444b.jpeg",
        "SV_cloud/result/case1_group10_689b0c58bc6eb25325b71d26.jpeg",
        "SV_cloud/result/case1_group10_689b0c567a433b7206d575bc.jpeg",
        "SV_cloud/result/case1_group10_689b0c597a433b7206d575bd.jpeg",
        "SV_cloud/result/case1_group10_689b0c707a433b7206d575be.jpeg",],

        ["SV_cloud/result/case1_group11_689b11d759bb23aae1ab35f9.jpeg",],

        ["SV_cloud/result/case1_group12_689b133b892992d6ea114454.jpeg",
        "SV_cloud/result/case1_group12_689b135a59bb23aae1ab3601.jpeg",
        "SV_cloud/result/case1_group12_689b135dbc6eb25325b71d35.jpeg",
        "SV_cloud/result/case1_group12_689b1388bc6eb25325b71d36.jpeg",
        "SV_cloud/result/case1_group12_689b13217a433b7206d575c9.jpeg",
        "SV_cloud/result/case1_group12_689b13227a433b7206d575ca.jpeg",
        "SV_cloud/result/case1_group12_689b13277a433b7206d575cb.jpeg",
        "SV_cloud/result/case1_group12_689b13807a433b7206d575cd.jpeg",
        "SV_cloud/result/case1_group12_689b1324892992d6ea114453.jpeg",],

        ["SV_cloud/result/case1_group13_689b14cd59bb23aae1ab3607.jpeg",],

        ["SV_cloud/result/case1_group14_689b16b17a433b7206d575dd.jpeg",
        "SV_cloud/result/case1_group14_689b16b059bb23aae1ab360c.jpeg",
        "SV_cloud/result/case1_group14_689b16c77a433b7206d575de.jpeg",
        "SV_cloud/result/case1_group14_689b16c959bb23aae1ab360f.jpeg",
        "SV_cloud/result/case1_group14_689b16c8892992d6ea11446f.jpeg",],

        ["SV_cloud/result/case1_group15_689b17a8bc6eb25325b71d44.jpeg",
        "SV_cloud/result/case1_group15_689b17b0bc6eb25325b71d45.jpeg",
        "SV_cloud/result/case1_group15_689b17b759bb23aae1ab3612.jpeg",
        "SV_cloud/result/case1_group15_689b17be892992d6ea114473.jpeg",],

        ["SV_cloud/result/case1_group16_689b1aa4bc6eb25325b71d4a.jpeg",
        "SV_cloud/result/case1_group16_689b1aa37a433b7206d575e8.jpeg",
        "SV_cloud/result/case1_group16_689b1aa6892992d6ea11447f.jpeg",],

        ["SV_cloud/result/case1_group17_689b2012bc6eb25325b71d59.jpeg",
        "SV_cloud/result/case1_group17_689b2028bc6eb25325b71d5a.jpeg",
        "SV_cloud/result/case1_group17_689b2029bc6eb25325b71d5b.jpeg",
        "SV_cloud/result/case1_group17_689b20297a433b7206d575f9.jpeg",
        "SV_cloud/result/case1_group17_689b201259bb23aae1ab3629.jpeg",
        "SV_cloud/result/case1_group17_689b2022892992d6ea11448b.jpeg",
        "SV_cloud/result/case1_group17_689b2022892992d6ea11448c.jpeg",
        "SV_cloud/result/case1_group17_689b2022892992d6ea11448d.jpeg",],

        ["SV_cloud/result/case1_group18_689b20e6892992d6ea114492.jpeg",
        "SV_cloud/result/case1_group18_689b20f5892992d6ea114493.jpeg",],

        ["SV_cloud/result/case1_group19_689b275d7a433b7206d57606.jpeg",
        "SV_cloud/result/case1_group19_689b275d59bb23aae1ab3632.jpeg",
        "SV_cloud/result/case1_group19_689b275e59bb23aae1ab3633.jpeg",
        "SV_cloud/result/case1_group19_689b2759bc6eb25325b71d69.jpeg",
        "SV_cloud/result/case1_group19_689b275859bb23aae1ab3631.jpeg",],

        ["SV_cloud/result/case1_group20_689b29a0bc6eb25325b71d70.jpeg",],

        ["SV_cloud/result/case1_group21_689b2ad9892992d6ea1144a4.jpeg",],

        ["SV_cloud/result/case1_group22_689b2dca7a433b7206d57612.jpeg",
        "SV_cloud/result/case1_group22_689b2dde892992d6ea1144aa.jpeg",
        "SV_cloud/result/case1_group22_689b2ddebc6eb25325b71d80.jpeg",],

        ["SV_cloud/result/case1_group23_689b322bbc6eb25325b71d92.jpeg",
        "SV_cloud/result/case1_group23_689b322c892992d6ea1144b8.jpeg",
        "SV_cloud/result/case1_group23_689b322dbc6eb25325b71d93.jpeg",],

        ["SV_cloud/result/case1_group24_689b3895bc6eb25325b71da3.jpeg",
        "SV_cloud/result/case1_group24_689b389359bb23aae1ab3663.jpeg",],

        ["SV_cloud/result/case1_group25_689b424cbc6eb25325b71dbb.jpeg",],

        ["SV_cloud/result/case1_group26_689b49007a433b7206d57661.jpeg",],

        ["SV_cloud/result/case1_group27_689b5384bc6eb25325b71de6.jpeg",],

        ["SV_cloud/result/case1_group28_689b569abc6eb25325b71def.jpeg",
        "SV_cloud/result/case1_group28_689b5695bc6eb25325b71dee.jpeg",
        "SV_cloud/result/case1_group28_689b56997a433b7206d57681.jpeg",
        "SV_cloud/result/case1_group28_689b569759bb23aae1ab36ad.jpeg",],

        ["SV_cloud/result/case1_group29_689b5bccbc6eb25325b71dfa.jpeg",
        "SV_cloud/result/case1_group29_689b5bce59bb23aae1ab36b2.jpeg",],

        ["SV_cloud/result/case1_group30_689c12dddf979a2f7bb0c195.jpeg",],

        ["SV_cloud/result/case1_group31_689c13b9df979a2f7bb0c199.jpeg",],

        ["SV_cloud/result/case1_group32_689c1557ff51ad28e2c21984.jpeg",
        "SV_cloud/result/case1_group32_689c155922a8aaf3744d41ad.jpeg",],

        ["SV_cloud/result/case1_group33_689c187edce991a403d5df9a.jpeg",],

        ["SV_cloud/result/case1_group34_689c1d78ff51ad28e2c2198f.jpeg",
        "SV_cloud/result/case1_group34_689c1d79dce991a403d5dfa1.jpeg",],

        ["SV_cloud/result/case1_group35_689c35d8ff51ad28e2c219a1.jpeg",
        "SV_cloud/result/case1_group35_689c35da22a8aaf3744d41ce.jpeg",
        "SV_cloud/result/case1_group35_689c35dc22a8aaf3744d41cf.jpeg",
        "SV_cloud/result/case1_group35_689c35dd22a8aaf3744d41d0.jpeg",
        "SV_cloud/result/case1_group35_689c35dfdf979a2f7bb0c1b8.jpeg",],

        ["SV_cloud/result/case1_group36_689c4c3dff51ad28e2c219c5.jpeg",
        "SV_cloud/result/case1_group36_689c4c40dce991a403d5dfc7.jpeg",
        "SV_cloud/result/case1_group36_689c4c3922a8aaf3744d41e9.jpeg",],

        ["SV_cloud/result/case1_group37_689c4e30df979a2f7bb0c1d3.jpeg",
        "SV_cloud/result/case1_group37_689c4e31df979a2f7bb0c1d4.jpeg",
        "SV_cloud/result/case1_group37_689c4e3322a8aaf3744d41f0.jpeg",],

        ["SV_cloud/result/case1_group38_689c628a22a8aaf3744d420b.jpeg",
        "SV_cloud/result/case1_group38_689c628bff51ad28e2c219ed.jpeg",],

        ["SV_cloud/result/case1_group39_689c69a6dce991a403d5dfe6.jpeg",
        "SV_cloud/result/case1_group39_689c69a122a8aaf3744d4213.jpeg",],

        ["SV_cloud/result/case1_group40_689c69f0ff51ad28e2c219fb.jpeg",
        "SV_cloud/result/case1_group40_689c69fadf979a2f7bb0c1ea.jpeg",],

        ["SV_cloud/result/case1_group41_689c6ceadf979a2f7bb0c1f8.jpeg",
        "SV_cloud/result/case1_group41_689c6cfbff51ad28e2c21a02.jpeg",
        "SV_cloud/result/case1_group41_689c6cfdff51ad28e2c21a04.jpeg",
        "SV_cloud/result/case1_group41_689c6cffdce991a403d5dfec.jpeg",
        "SV_cloud/result/case1_group41_689c6d30df979a2f7bb0c1fe.jpeg",],

        ["SV_cloud/result/case1_group42_689c705cff51ad28e2c21a16.jpeg",
        "SV_cloud/result/case1_group42_689c705d22a8aaf3744d422d.jpeg",
        "SV_cloud/result/case1_group42_689c7059dce991a403d5dff3.jpeg",],

        ["SV_cloud/result/case1_group43_689c7204dce991a403d5dffb.jpeg",],

        ["SV_cloud/result/case1_group44_689c750cdf979a2f7bb0c218.jpeg",
        "SV_cloud/result/case1_group44_689c751e22a8aaf3744d423c.jpeg",
        "SV_cloud/result/case1_group44_689c753bdf979a2f7bb0c21b.jpeg",
        "SV_cloud/result/case1_group44_689c7526df979a2f7bb0c21a.jpeg",
        "SV_cloud/result/case1_group44_689c7526ff51ad28e2c21a20.jpeg",],

        ["SV_cloud/result/case1_group45_689c75cfff51ad28e2c21a23.jpeg",
        "SV_cloud/result/case1_group45_689c75dadce991a403d5e007.jpeg",
        "SV_cloud/result/case1_group45_689c75efdf979a2f7bb0c21f.jpeg",
        "SV_cloud/result/case1_group45_689c75f122a8aaf3744d4243.jpeg",],

        ["SV_cloud/result/case1_group46_689c78f5ff51ad28e2c21a2b.jpeg",
        "SV_cloud/result/case1_group46_689c78fcdce991a403d5e012.jpeg",
        "SV_cloud/result/case1_group46_689c7911ff51ad28e2c21a2d.jpeg",
        "SV_cloud/result/case1_group46_689c7926dce991a403d5e013.jpeg",],
    ]
    
    for images in images_groups:
        main(images)