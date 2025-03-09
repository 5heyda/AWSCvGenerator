from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel
import httpx
import os
import tempfile
from dotenv import load_dotenv
from weasyprint import HTML  # Replace pdfkit with WeasyPrint

# Load environment variables
load_dotenv()

app = FastAPI()

# Set up templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Models
class ResumeRequest(BaseModel):
    markdown: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/resume", response_class=HTMLResponse)
async def resume(request: Request):
    return templates.TemplateResponse("resume.html", {"request": request})

@app.get("/resume-pdf")
async def resume_pdf():
    """Generate and download a PDF version of the resume"""
    try:
        # Get the HTML content
        html_content = templates.get_template("resume.html").render({"request": {"base_url": ""}})
        
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf_path = tmp.name
        
        # Generate PDF from HTML using WeasyPrint
        HTML(string=html_content).write_pdf(pdf_path)
        
        # Return the PDF file
        return FileResponse(
            path=pdf_path, 
            filename="resume.pdf", 
            media_type="application/pdf",
            background=lambda: os.unlink(pdf_path)  # Delete the file after sending
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.get("/resume-builder", response_class=HTMLResponse)
async def resume_builder(request: Request):
    print("Resume builder route accessed")
    return templates.TemplateResponse("resume_builder.html", {"request": request})

@app.post("/api/generate-resume")
async def generate_resume(resume_request: ResumeRequest):
    # Get API key from environment variable
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        raise HTTPException(status_code=500, detail="API key not configured")
    
    # Prepare the prompt for Claude
    prompt = f"""
You are an expert resume designer. I want you to create an HTML resume based on the markdown content I provide.
Use the same styling and structure as the sample resume I showed you earlier, with a modern, professional design.

The resume should have:
1. A header with name, title, and contact links
2. A skills section with styled skill bubbles
3. A portfolio section with project cards
4. An experience section with a timeline layout
5. Responsive design that works on all devices

Here's the markdown content to convert:

{resume_request.markdown}

Return ONLY the complete HTML code for the resume, including all necessary CSS inline in a <style> tag.
The HTML should be ready to save as a standalone file that can be opened in any browser.
"""

    # Set the correct API version
    api_version = "2023-06-01"
    print(f"Using API version: {api_version}")
    
    # Call Claude API
    try:
        print(f"Making API request to Claude with API key: {api_key[:4]}...")
        
        headers = {
            "x-api-key": api_key,
            "anthropic-version": api_version,
            "content-type": "application/json"
        }
        
        # Print the headers to verify
        print(f"Request headers: {headers}")
        
        # Use a faster model and increase timeout
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json={
                    "model": "claude-3-haiku-20240307",  # Using a faster model
                    "max_tokens": 4000,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=120.0  # Increase timeout to 2 minutes
            )
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                error_detail = f"Error from AI service: {response.status_code}"
                try:
                    error_body = response.json()
                    error_detail += f" - {error_body}"
                except:
                    error_detail += f" - {response.text}"
                
                print(f"API Error: {error_detail}")
                raise HTTPException(status_code=response.status_code, detail=error_detail)
            
            result = response.json()
            html_content = result["content"][0]["text"]
            
            # Clean up the HTML content if needed
            if html_content.startswith("```html") and html_content.endswith("```"):
                html_content = html_content[7:-3].strip()
            
            return JSONResponse(content={"html": html_content})
    
    except httpx.ReadTimeout:
        print("Request to Claude API timed out")
        raise HTTPException(
            status_code=504, 
            detail="The request to the AI service timed out. Please try again with simpler content or try later."
        )
    except Exception as e:
        print(f"Exception in generate_resume: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{name}")
async def greet(request: Request, name: str):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "name": name}
    )

@app.post("/api/test-claude")
async def test_claude():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return JSONResponse(content={"error": "API key not configured"})
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 100,
                    "messages": [{"role": "user", "content": "Say hello"}]
                }
            )
            
            return JSONResponse(content={
                "status": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            })
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.post("/api/generate-pdf")
async def generate_pdf(request: dict):
    """Generate a PDF from HTML content"""
    try:
        html_content = request.get("html")
        if not html_content:
            raise HTTPException(status_code=400, detail="HTML content is required")
        
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf_path = tmp.name
        
        # Generate PDF from HTML using WeasyPrint
        HTML(string=html_content).write_pdf(pdf_path)
        
        # Return the PDF file
        return FileResponse(
            path=pdf_path, 
            filename="resume.pdf", 
            media_type="application/pdf",
            background=lambda: os.unlink(pdf_path)  # Delete the file after sending
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
