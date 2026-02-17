import pandas as pd

class compareRelease():
    """A function that takes two release files - on initiation compares the aggregates of different fields
    Can be used for metadata or release depending on the specified fields"""
    def __init__(self, release1_csv, release2_csv, sum_fields = [], dist_count_fields = [], bidi_data = False):
        self.release1 = pd.read_csv(release1_csv, sep="\t")
        self.release2 = pd.read_csv(release2_csv, sep="\t")


        self.bidi_data = bidi_data

        # Perform the aggregration and store the aggregated stats in a dictionary
        self.agg_stats = {}
        for field in sum_fields:
            self.agg_stats[field] = self.compare_field_sum(field)
        
        for field in dist_count_fields:
            self.agg_stats[field] = self.compare_field_dist(field)
        

    
    def compare_field_sum(self, field):
        """Compare the sum of a specified across the datasets"""
        sum1 = self.release1[field].sum()
        sum2 = self.release2[field].sum()
        return {"release1": sum1, "release2": sum2, "diff": sum2-sum1}

    def compare_field_dist(self, field):
        """Compare the distinct count of values for a field specified in the dataset"""
        if field == "all_data":
            dist1 = len(self.release1.drop_duplicates())
            dist2 = len(self.release2.drop_duplicates())
            if self.bidi_data:
                #If we're dealing with a bidirectional reuse dataset divide the unique value count by 2
                dist1 = dist1 / 2
                dist2 = dist2/ 2
        else:
            dist1 = len(self.release1[field].drop_duplicates())
            dist2 = len(self.release2[field].drop_duplicates())
        return {"release1": dist1, "release2": dist2, "diff": dist2-dist1}
    
    # Function to fetch new ids - present in one dataset not other
    def fetch_new_data(self, field="book1"):
        old_ids = self.release1[field].to_list()
        new_ids_df = self.release2[~self.release2[field].isin(old_ids)]
        return new_ids_df
    
    def aggregate_new_data(self, field="total", agg_type="dist", return_top = 0, id_field="book1"):
        """If return_top is set to 0 then the function will return all data, otherwise it will return a list of 
        ids and aggregrate stats for the top n up to the specified amount - e.g. 5 will return the top 5 uris for the
        chosen aggregation"""
        if agg_type not in ["dist", "sum"]:
            print("Specify a correct type of aggregation field. For a sum - 'sum', for a distinct count 'dist'")
            return None
        else:
            new_ids_df = self.fetch_new_data(field=id_field)
            new_ids_list = new_ids_df[id_field].drop_duplicates().dropna().to_list()
            
            dict_for_df = []
            for new_id in new_ids_list:
                filtered_df = new_ids_df[new_ids_df[id_field]==new_id]
                id = filtered_df["_T1"].to_list()[0]
                if field == "total":
                    count = len(filtered_df)
                else:
                    if agg_type == "dist":
                        count = len(filtered_df[field].drop_duplicates())
                    elif agg_type == "sum":
                        count = filtered_df[field].sum()
                dict_for_df.append({"id": new_id, "count": count, "vers_id": id})
            df_out = pd.DataFrame(dict_for_df)
            df_out = df_out.sort_values(by=["count"], ascending=False)
            if return_top != 0:
                df_out = df_out.loc[:return_top-1]
            
            return df_out

                


        

