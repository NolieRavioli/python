import html, json, os, datetime
from zoneinfo import ZoneInfo  # Available in Python 3.9+

def format_html(text):
    output_parts = []  # collect formatted parts here

    # 1. Handle [code] blocks separately
    while "[code]" in text and "[/code]" in text:
        before, code_block, after = text.split("[code]", 1)[0], None, None
        rest = text.split("[code]", 1)[1]
        if "[/code]" in rest:
            code_block, after = rest.split("[/code]", 1)
        else:
            code_block = rest
            after = ""
        if before:
            output_parts.append(format_text(before))
        escaped_code = html.escape(code_block, quote=True)
        escaped_code = escaped_code.replace("\t", "    ").replace("\n", "<br>")
        output_parts.append(f"<code>{escaped_code}</code>")
        text = after
    if text:
        output_parts.append(format_text(text))
    
    # Generate timestamp using the America/Denver timezone
    timestamp = datetime.datetime.now(ZoneInfo("America/Denver")).strftime("%Y-%m-%d %H:%M:%S %Z")
    
    # Wrap content in a div and include timestamp inside at the bottom right.
    formatted = (
      "<div class=\"textPost\" style=\"position: relative; padding-bottom: 1.2em;\">"
      + "".join(output_parts)
      + f"<p class=\"timestamp\" style=\"position: absolute; bottom: 0; right: 0; margin: 0; font-size:0.8rem; color:#555;\">Posted on {timestamp}</p>"
      + "</div>"
    )
    return formatted

def format_text(raw_text):
    formatted = ""
    # Split text into paragraphs by blank lines (double newline)
    paragraphs = [para.strip() for para in raw_text.split("\n\n") if para.strip() != ""]
    for para in paragraphs:
        # Replace BBCode-style formatting tags with HTML tags
        para = para.replace("[b]", "<b>").replace("[/b]", "</b>") \
                   .replace("[i]", "<i>").replace("[/i]", "</i>") \
                   .replace("[u]", "<u>").replace("[/u]", "</u>") \
                   .replace("[s]", "<s>").replace("[/s]", "</s>")
        # Handle links
        if "[url]" in para and "[/url]" in para:
            para = para.replace("[newTab]", "target='_blank'")
            para = para.replace("[url]", "<a href='").replace("[/link]", "'>") \
                       .replace("[/url]", "</a>")
        # Handle lists
        if "[list]" in para and "[/list]" in para:
            list_content = para.split("[list]", 1)[1].split("[/list]", 1)[0]
            items_html = ""
            for item in list_content.splitlines():
                item = item.strip()
                if item.startswith("[*]"):
                    item_text = item[len("[*]"):].strip()
                    item_text = html.escape(item_text, quote=True)
                    items_html += f"<li>{item_text}</li>"
            para = para.split("[list]")[0] + f"<ul>{items_html}</ul>" + para.split("[/list]")[1]
        # Escape any remaining characters
        para = html.escape(para, quote=True)
        formatted += f"<p>{para}</p>"
    return formatted

def lambda_handler(event, context):
    http_method = event.get("httpMethod", event.get("method", ""))
    if http_method == "GET":
        # Process GET as before
        path = event["path"]
        if path != '/':
            path_parts = path.split('/')
            if path[0] == '/':
                path_parts = path_parts[1:]
            file_path = os.path.join(os.path.dirname(__file__), "www", *path_parts, "index.html")
        else:
            file_path = os.path.join(os.path.dirname(__file__), "www", "index.html")
    
        try:
            with open(file_path, "r") as f:
                html_content = f.read()
            return {
                "statusCode": 200,
                "headers": { "Content-Type": "text/html" },
                "body": html_content
            }
        except FileNotFoundError:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "text/plain"},
                "body": "404 Not Found"
            }
    elif http_method == "POST":
        try:
            if event["path"] == "/login/auth":
                data = json.loads(event["body"] or "{}")
                username = data.get("username")
                password = data.get("password")
                # Validate credentials
                if username in os.environ and password == os.environ[username]:
                    post_text = data.get("content", "")
                    formatted_html = format_html(post_text)
                    return {
                        "statusCode": 200,
                        "headers": { "Content-Type": "text/plain" },
                        "body": formatted_html
                    }
                else:
                    return { "statusCode": 401, "body": "Unauthorized" }
        except Exception as e:
            return { "statusCode": 500, "body": str(e) }
