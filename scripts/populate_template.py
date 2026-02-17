from compare_releases import compareRelease
import re
import yaml

# Field dict - specifying the field and the corresponding tag to replace in the template
# all_data field tells the compareRelease obj to return a total count of rows in the compared
# dfs
field_dict = {"instances" : {"count_tag": "@INST-ST@", 
                    "change_tag": "@INST-CH@",
                    "data" : "reuse",
                    "agg_type": "sum"
                    },
                "WM1_Total" : {"count_tag": "@WM-ST@", 
                    "change_tag": "@WM-CH@",
                    "data" : "reuse",
                    "agg_type": "sum"
                    },
                "book" : {"count_tag": "@BC-ST@", 
                    "change_tag": "@BC-CH@",
                    "data" : "meta",
                    "agg_type": "dist"
                    },
                "all_data" : {"count_tag": "@PW-ST@", 
                    "change_tag": "@PW-CH@",
                    "data" : "reuse",
                    "agg_type": "dist"
                    },
}

# Field pattern for populating URI field - specifying the field to use for aggregation
uri_fields = {"tags": {"url": {"pre-numeral": "@URLID", "post-numeral": "@"},
            "uri": {"pre-numeral": "@0000AUTHOR.BOOK.ID", "post-numeral": "@"},
            "uri_data": {"pre-numeral" : "@id", "post-numeral" : "data@"}},
            "data_field": "instances"}

# Function to replease a uri tag
def replace_uri_id(text, id_no, tag_type, replacement, uri_fields=uri_fields["tags"]):
    tags = uri_fields[tag_type]
    regex = f"{tags['pre-numeral']}{id_no}{tags['post-numeral']}"
    replacement = str(replacement)
    text = re.sub(regex, replacement, text)
    return text

# # Function to use a df of URIs and data to populate email
def uri_df_to_email(text, df,  vers_code):

    data_dict = df.to_dict("records")
    for idx, data in enumerate(data_dict):
        vers_uri = data["vers_id"]
        url = f"https://kitab-project.org/explore/#/visualise/{vers_code}/?books={vers_uri}"
        id_no = idx+1
        text = replace_uri_id(text, id_no, "url", url)
        text = replace_uri_id(text, id_no, "uri", data["id"])
        text = replace_uri_id(text, id_no, "uri_data", data["count"])
    
    return text

    



# Function to replace fields in template
def replace_stat_tag(text, tag, replacement):
    replacement = "{:,}".format(replacement)
    
    return re.sub(tag, replacement, text)


def populate_template(template_text, config_dict, field_dict):
    """Use the uri_fields dict to populate the template"""


    # Create fields from the field_dict
    reuse_sum_fields = []
    reuse_dist_fields = []
    meta_sum_fields = []
    meta_dist_fields = []
    for data_type, config in field_dict.items():
        if config["data"] == "reuse":
            if config["agg_type"] == "sum":
                reuse_sum_fields.append(data_type)
            elif config["agg_type"] == "dist":
                reuse_dist_fields.append(data_type)
        elif config["data"] == "meta":
            if config["agg_type"] == "sum":
                meta_sum_fields.append(data_type)
            elif config["agg_type"] == "dist":
                meta_dist_fields.append(data_type)
    
    reuse_compare = compareRelease(config_dict["prev_release"]["reuse_uni"], config_dict["latest_release"]["reuse_uni"], sum_fields=reuse_sum_fields, dist_count_fields=reuse_dist_fields)
    meta_compare = compareRelease(config_dict["prev_release"]["meta"], config_dict["latest_release"]["meta"], sum_fields=meta_sum_fields, dist_count_fields=meta_dist_fields)

    for data_type, config in field_dict.items():
        if config["data"] == "reuse":
            data = reuse_compare
        elif config["data"] == "meta":
            data = meta_compare
        template_text = replace_stat_tag(template_text, config["count_tag"], data.agg_stats[data_type]["release2"])
        template_text = replace_stat_tag(template_text, config["change_tag"], data.agg_stats[data_type]["diff"])
    
    # Perform replacements for the uri-specific data
    reuse_bidir = compareRelease(config_dict["prev_release"]["reuse_bi"], config_dict["latest_release"]["reuse_bi"])
    top_df = reuse_bidir.aggregate_new_data(return_top=4)
    template_text = uri_df_to_email(template_text, top_df, config_dict["new_vers_code"])
    
    return template_text

def create_email_html(template_path, out_html, config_yaml, field_dict):

    # Open config yaml and store as dict
    with open(config_yaml) as f:
        config_dict = yaml.load(f, Loader=yaml.SafeLoader)

    with open(template_path, "r") as f:
        template_text = f.read()
    
    print(config_dict)
    
    written_template = populate_template(template_text, config_dict, field_dict)

    with open(out_html, "w") as f:
        f.write(written_template)


if __name__ == "__main__":

    # reuse_tsvs = {"release1": "E:/Corpus Stats/2023/stats/stats-v8_uni-dir.csv",
    #               "release2": "E:/Corpus Stats/2025/stats/book-stats_uni-dir_2025-1-9.csv"}
    
    # meta_tsvs = {"release1": "E:/Corpus Stats/2023/OpenITI_metadata_2023-1-8.csv",
    #              "release2": "E:/Corpus Stats/2025/OpenITI_metadata_2025-1-9.tsv"}

    template_path = "../templates/rendered_template_4.html"
    out_html = "../written_html/test_email.html"
    config_yml = "config_newsletter.yml"

    create_email_html(template_path, out_html, config_yml, field_dict)