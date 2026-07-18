import os
import pandas as pd
import logging
import chardet

logger = logging.getLogger(__name__)

def analyze_dataset(file_path: str) -> dict:
    try:
        # Try to detect encoding first
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
        
        logger.info(f"Detected encoding: {encoding} for file: {file_path}")
        
        # Try reading with detected encoding, fallback to others
        try:
            df = pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            logger.warning(f"Encoding {encoding} failed, trying utf-8")
            df = pd.read_csv(file_path, encoding='utf-8')
        except Exception:
            logger.warning(f"UTF-8 failed, trying latin-1")
            df = pd.read_csv(file_path, encoding='latin-1')

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)  # in bytes
        total_rows = len(df)
        headers = list(df.columns)
        shape = f"{total_rows} rows, {len(headers)} columns"

        # Generate detailed metadata for each column
        metadata = []
        for column in df.columns:
            dtype = str(df[column].dtype)
            missing = int(df[column].isnull().sum())  # Convert numpy.int64 to Python int
            metadata.append({
                "column": column,
                "dtype": dtype,
                "missing": missing
            })

        # Suggest target column (first non-id column)
        suggested_target = None
        for col in df.columns:
            if col.lower() not in ['id', 'index', 'timestamp'] and df[col].dtype in ['int64', 'float64']:
                suggested_target = col
                break
        if suggested_target is None and len(df.columns) > 0:
            suggested_target = df.columns[0]

        # Convert preview (first 5 rows) into list of lists with native Python types
        preview_rows = []
        for _, row in df.head().iterrows():
            preview_rows.append([x.item() if hasattr(x, 'item') else x for x in row])

        return {
            "fileName": file_name,
            "fileSize": file_size,
            "totalRows": total_rows,
            "headers": headers,
            "rows": preview_rows,
            "columns": headers,  # Alias for headers to match generate.py expectation
            "metadata": metadata,
            "shape": shape,
            "suggested_target": suggested_target
        }

    except pd.errors.EmptyDataError:
        logger.error(f"Empty CSV file: {file_path}")
        raise RuntimeError("The CSV file appears to be empty. Please upload a valid CSV file with data.")
    
    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing error in {file_path}: {str(e)}")
        raise RuntimeError(f"CSV parsing error: {str(e)}. Please check your CSV file format.")
    
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error in {file_path}: {str(e)}")
        raise RuntimeError("Encoding error. Please ensure your CSV file uses UTF-8 encoding.")
    
    except Exception as e:
        logger.error(f"Unexpected error analyzing dataset {file_path}: {str(e)}")
        raise RuntimeError(f"Error analyzing dataset: {str(e)}")
