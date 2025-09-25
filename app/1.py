from pymilvus import connections, utility

# Connect to Milvus
connections.connect("default", host="127.0.0.1", port="19530")

# ✅ List all collections
print("Collections:", utility.list_collections())



# ✅ Drop a collection
utility.drop_collection("rag_demo_local")
print("Dropped rag_demo_local")

# ✅ Verify again
print("Collections after drop:", utility.list_collections())
