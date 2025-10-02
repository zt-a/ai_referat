from ai_referat.docx_writer import create_docx_file_for_json

create_docx_file_for_json(
    docx_path="./results/docx/ref.docx", 
    json_path="./results/json/referat_История HTML.json", 
    content_font="Times New Roman",
    content_size=14
)