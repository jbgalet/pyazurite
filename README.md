# PyAzurite
Very basic implementation of Azure Blob Storage

The purpose of this tool is to allow MSSQL BULK INSERT from an inaccessible drive like `\\tsclient`.

To use the tool:
 * edit the `data_folder` path in `app.py`
 * get a valid certificate (trusted by the computer) for a hostname, edit `KEY_PATH` and `CERT_PATH`

n.b. the external storage don't accept uris with a port description, the tool has to run on port 443.

## MSSQL Example
```tsql
--- [Optional] Drop the existing data source
DROP EXTERNAL DATA SOURCE PyAzurite;
GO

--- Add the external data source
CREATE EXTERNAL DATA SOURCE PyAzurite
    WITH (   
        TYPE = BLOB_STORAGE,  
        LOCATION = 'https://FIXME/blob'
    )  
GO

--- Test with CSV
SELECT * FROM OPENROWSET(
   BULK  'test.csv',
   DATA_SOURCE = 'PyAzurite',
   SINGLE_CLOB) AS DataFile;

--- BULK INSERT With data and format file
--- n.b. the documentation mistyped FORMATFILE_DATA_SOURCE
BULK INSERT [domain_user]
   FROM 'myfile.tsv'
   WITH
   (
	  DATA_SOURCE = 'PyAzurite',
	  FORMATFILE_DATA_SOURCE = 'PyAzurite',
      FORMATFILE = 'myformat.fmt',
      DATAFILETYPE = 'widechar',
      CODEPAGE = 'RAW',
      ROWS_PER_BATCH = 1,
      BATCHSIZE = 1000000,
      MAXERRORS = 10000,
      TABLOCK
   );
```