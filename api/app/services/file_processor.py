import io

import pandas as pd


def process_file(content: bytes, extension: str) -> pd.DataFrame:
    """Parse uploaded file content into a pandas DataFrame."""
    buffer = io.BytesIO(content)

    if extension == ".csv":
        # Try common encodings
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                buffer.seek(0)
                return pd.read_csv(buffer, encoding=encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("Unable to decode CSV file. Please check the file encoding.")

    if extension == ".xlsx":
        return pd.read_excel(buffer, engine="openpyxl")

    raise ValueError(f"Unsupported file extension: {extension}")
