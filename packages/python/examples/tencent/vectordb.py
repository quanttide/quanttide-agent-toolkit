import tcvectordb
from tcvectordb.model.enum import FieldType, IndexType, MetricType, EmbeddingModel, ReadConsistency
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams
from tcvectordb.model.enum import FieldType, IndexType, MetricType, ReadConsistency


#create a database client object
client = tcvectordb.VectorDBClient(url='http://10.0.X.X', username='root', key='eC4bLRy2va******************************', read_consistency=ReadConsistency.EVENTUAL_CONSISTENCY, timeout=30)
# create a database
db = client.create_database(database_name='db-test')

print(db.database_name)


#create a database client object
client = tcvectordb.VectorDBClient(url='http://10.0.X.X', username='root', key='eC4bLRy2va******************************', read_consistency=ReadConsistency.EVENTUAL_CONSISTENCY, timeout=30)

db = client.database('db-test')

# -- index config
# 第一步，设计索引（不是设计 Collection 的结构）
# 1. 【重要的事】向量对应的文本字段不要建立索引，会浪费较大的内存，并且没有任何作用。
# 2. 【必须的索引】：主键id、向量字段 vector 这两个字段目前是固定且必须的，参考下面的例子。
# 3. 【其他索引】：检索时需作为条件查询的字段，比如要按书籍的作者进行过滤，这个时候 author 字段就需要建立索引，
#     否则无法在查询的时候对 author 字段进行过滤，不需要过滤的字段无需加索引，会浪费内存；
# 4.  向量数据库支持动态 Schema，写入数据时可以写入任何字段，无需提前定义，类似 MongoDB.
# 5.  例子中创建一个书籍片段的索引，例如书籍片段的信息包括 {id, vector, bookName, author，},
#     id 为主键需要全局唯一，vector 字段需要建立向量索引，假如我们在查询的时候要查询指定书名称的内容，这个时候需要对 bookName 建立索引，其他字段没有条件查询的需要，无需建立索引。
index = Index(
            FilterIndex(name='id', field_type=FieldType.String, index_type=IndexType.PRIMARY_KEY),
            FilterIndex(name='author', field_type=FieldType.String, index_type=IndexType.FILTER),
            FilterIndex(name='bookName', field_type=FieldType.String, index_type=IndexType.FILTER),
            VectorIndex(name='vector', dimension=3, index_type=IndexType.HNSW,
                        metric_type=MetricType.COSINE, params=HNSWParams(m=16, efconstruction=200))
        )

# create a collection
# 第二步，创建 Collection
coll = db.create_collection(
            name='book-vector',
            shard=1,
            replicas=2,
            description='this is a collection of test embedding',
            index=index
        )

print(vars(coll))
