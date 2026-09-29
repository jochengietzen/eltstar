import pyarrow as pa

schema = pa.schema([("some_int", pa.int32()), ("some_string", pa.string())])

print([field.nullable for field in schema])
