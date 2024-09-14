from fastapi import HTTPException

# Define reusable HTTPExceptions
SummaryNotFoundException = HTTPException(status_code=404, detail="Summary not found; please try another ID")
