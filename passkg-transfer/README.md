# 整体目标

1. 实现查询Pg数据库方法，将结果映射成list[map[string,any]]格式【完成】
```sql
CREATE TABLE lightrag_doc_full (
	id varchar(255) NOT NULL,
	workspace varchar(255) NOT NULL,
	doc_name varchar(1024) NULL,
	"content" text NULL,
	meta jsonb NULL,
	create_time timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	update_time timestamp NULL,
	CONSTRAINT lightrag_doc_full_pk PRIMARY KEY (workspace,id)
);
CREATE TABLE lightrag_doc_chunks (
	id varchar(255) NOT NULL,
	workspace varchar(255) NOT NULL,
	full_doc_id varchar(256) NULL,
	chunk_order_index int4 NULL,
	tokens int4 NULL,
	"content" text NULL,
	content_vector public.vector NULL,
	file_path text NULL,
	create_time timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	update_time timestamp NULL,
	llm_cache_list jsonb DEFAULT '[]'::jsonb NULL,
	CONSTRAINT lightrag_doc_chunks_pk PRIMARY KEY (workspace, id)
);
```
2. 实现写入pg数据库方法，写入数据采用list[map[string,any]]格式，如：[{"id":"xxx", "name": "xx", "content": "xxx"},{}]【完成】
```sql
CREATE TABLE public.documents (
	id varchar(36) NOT NULL,
	"content" text NOT NULL,
	extraction_prompt text NULL,
	workspace_id text NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	chunks int4 NULL,
	parent varchar NULL,
	is_project_doc bool DEFAULT false NULL,
	last_mod time NULL,
	process_status varchar NULL,
	"name" varchar NULL,
	"type" varchar NULL,
	summary text NULL,
	tags _varchar NULL,
	CONSTRAINT documents_pkey PRIMARY KEY (id)
);
CREATE TABLE public.document_chunks (
	document_id text NOT NULL,
	chunk_index text NOT NULL,
	"text" text NOT NULL,
	embedding public.vector NULL,
	CONSTRAINT document_chunks_pkey PRIMARY KEY (document_id, chunk_index)
);
```
3. 实现数据转换方法，将第一步查出来的数据，通过映射转换，写入第二个数据源【完成】
```
lightrag_doc_full->documents
lightrag_doc_chunks->document_chunks
```
4. 读和写的PG数据源参数来自.env，读数据源LG_xxx，写数据源KG_xxx【完成】
5. lightrag_doc_full的doc_name为null,需要一个方法，基于lightrag_doc_chunks的file_path中截取名称后回写入lightrag_doc_full【完成】
6. 通过neo_exporter.py导出指定空间内所有的点和边,用json形式返回，连接参数见.env中的NEO4J_*
7. 通过utils.py中schema_mapper方法将json格式的点和边转换，通过save_to_csv方法，将点和边都存入csv，nebula的存储格式如下所示：
	```
	CREATE TAG IF NOT EXISTS entity(name string, type string, description string, ref string, created_at timestamp)
	CREATE EDGE IF NOT EXISTS relation(keywords string, description string, weight double, ref string)
	```
8. 通过nebula_import.py将点和边存入nebula,nebula使用参考 ../passkg-api-test/nebula.py中的使用，连接方式见.env中的NEBULA_*

# 代码结构
1. database.py 数据库连接管理和操作
2. operator_*.py 不同数据库需要的数据操作
3. utils.py 文件、数据映射操作
4. main.py 主函数入口，模块组合完成最终任务
5. neo_exporter.py neo4j导出任务
6. nebula_import.py nebula导入任务