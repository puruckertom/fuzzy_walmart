import mysql.connector as sql
import pandas as pd
import numpy as np
import os
#
# #Establish database connection. Parameters must be specified by the user
# db_connection = sql.connect(host='', database='', user='', password='')
#
# #get product table and productdocument table and merge the two
# prod_to_doc=pd.read_sql('SELECT product_id as prod_id, document_id FROM dashboard_productdocument', con=db_connection)
# products = pd.read_sql('SELECT id as prod_id, title, manufacturer, brand_name as brand FROM dashboard_product', con=db_connection)
# merged=prod_to_doc.merge(products, on="prod_id", how="left")
#
# #get datadocument table and merge with other tables
# data_docs=pd.read_sql('SELECT id as document_id, data_group_id FROM dashboard_datadocument' , con=db_connection)
# merged=merged.merge(data_docs, on ="document_id", how="left")
#
# #get datagroup table, merge with other tables, and  close database connection
# data_groups=pd.read_sql('SELECT id as data_group_id,data_source_id FROM dashboard_datagroup', con=db_connection)
# merged=merged.merge(data_groups, on="data_group_id", how="left")
#
# db_connection.close()
#
# #Keep only the products in the Walmart MSDS data source
# filtered=merged.loc[merged["data_source_id"]==10]
#
# filtered.brand=filtered.brand.str.lower().str.strip()

#Fuzzy Matching#################
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

filtered_copy=filtered
brands_copy=filtered_copy["brand"]
brands_copy=brands_copy.str.strip().str.lower()
brands_unique=list(set(brands_copy))

# brands_unique_series=pd.Series(brands_unique)
# brands_unique_series.to_csv("walmart_msds_unique_brands.csv", index=False)
# brands_unique_series=pd.read_csv("walmart_msds_unique_brands.csv", names=["brand"])

master=pd.DataFrame()
for brand in brands_unique:
    # print(brands_unique.index(brand))
    brands_unique=list(set(brands_copy))
    #removing the exact match
    brands_unique.remove(brand)
    #top 5 matches that are not exact
    token_sort_top_5=process.extract(brand, brands_unique, limit=5, scorer=fuzz.token_sort_ratio)
    token_set_top_5=process.extract(brand, brands_unique, limit=5, scorer=fuzz.token_set_ratio)
    partial_top_5=process.extract(brand, brands_unique, limit=5, scorer=fuzz.partial_ratio)

    token_sort=pd.DataFrame(token_sort_top_5, columns=["token_sort_brand","token_sort_score"])
    token_set=pd.DataFrame(token_set_top_5, columns=["token_set_brand","token_set_score"])
    partial=pd.DataFrame(partial_top_5, columns=["partial_ratio_brand","partial_ratio_score"])
    merged_scores=pd.concat([token_sort,token_set,partial], axis=1)
    merged_scores["original_brand"]=brand
    master=pd.concat([master,merged_scores], ignore_index=True)

master=master[["original_brand","token_sort_brand","token_sort_score","token_set_brand","token_set_score","partial_ratio_brand","partial_ratio_score"]]
# master.to_csv("walmart_msds_master_score.csv", index=False)

################################

# #only keep one unique combination of a document id and brand in the case of multiple products of the same brand in a single document
# filtered_drop_dups=filtered.drop_duplicates(subset=["document_id","brand"])
# filtered_drop_dups=filtered_drop_dups.reset_index()
# filtered_drop_dups=filtered_drop_dups.drop(columns=["index"])
#
# open_refine_test=filtered_drop_dups.head(int(len(filtered_drop_dups)/4))
# open_refine_test.to_csv("walmart_msds_open_refine_inpt.csv", columns=["document_id","title","brand"], index=False)
#
# #Create a df of document_ids that only have a single brand associated with it
# doc_id_counts=pd.DataFrame(filtered_drop_dups.document_id.value_counts())
# doc_id_counts["count"]=doc_id_counts["document_id"]
# doc_id_counts["document_id"]=doc_id_counts.index
# doc_id_counts=doc_id_counts.reset_index()
# doc_id_counts=doc_id_counts[["document_id","count"]]
# doc_id_counts=doc_id_counts.loc[doc_id_counts["count"]==1]
#
# #merge back all product information associated with each document_id
# brand_counts=doc_id_counts.merge(filtered_drop_dups, on="document_id", how="left")
#
# #See how many occurances of each brand there are and create a list of brands that occur at least 25 times
# brand_counts_filt=pd.DataFrame(brand_counts.brand.value_counts())
# brand_counts_filt["count"]=brand_counts_filt["brand"]
# brand_counts_filt["brand"]=brand_counts_filt.index
# brand_counts_filt=brand_counts_filt.reset_index()
# brand_counts_filt=brand_counts_filt[["brand","count"]]
# brand_counts_filt=brand_counts_filt.loc[brand_counts_filt["brand"]!="unknown"]
# brand_counts_filt=brand_counts_filt.loc[brand_counts_filt["count"]>24]
#
# brand_list=list(brand_counts_filt["brand"])
#
# #create final df of document_ids that have an associated brand in the list indicating occurance >=25 and sort by brand
# final=brand_counts.loc[brand_counts["brand"].isin(brand_list)]
# final=final.sort_values(by="brand")
# final=final.reset_index()
# final=final.drop(columns=["index"])
#
# # os.chdir("//home//lkoval//walmart_msds")
# # for brand in brand_list:
# #     final_brand=final.loc[final["brand"]==brand]
# #     final_brand=final_brand[["brand","document_id"]]
# #     final_brand.to_csv("%s.csv"%brand.lower().strip().replace(" ","_"), index=False)
