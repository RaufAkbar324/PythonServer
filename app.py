# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from bs4 import BeautifulSoup
# import re

# app = Flask(__name__)
# CORS(app)

# def extract_sections_from_html(html):
#     sections = html.split('#####')
#     sections = [s.strip() for s in sections]

#     head_html = sections[0] if len(sections) > 0 else ''
#     slug = sections[1] if len(sections) > 1 else ''
#     title = sections[2] if len(sections) > 2 else ''
#     text_body = sections[3] if len(sections) > 3 else ''
#     faq_html = sections[4] if len(sections) > 4 else ''

#     # Extract styles from full HTML
#     full_soup = BeautifulSoup(html, 'html.parser')
#     styles = full_soup.find_all('style')
#     style_block = ''.join(str(style) for style in styles)

#     # ✅ Ensure <a> tags have no underline and preserve <img> and <iframe>
#     soup_body = BeautifulSoup(text_body, 'html.parser')
#     for tag in soup_body.find_all(True):
#         if tag.name == 'a':
#             current_style = tag.get('style', '')
#             if 'text-decoration' not in current_style:
#                 current_style += '; text-decoration: none;'
#             tag['style'] = current_style
#     text_body = str(soup_body)

#     # ✅ Wrap text_body as a complete HTML document with styles
#     text_html = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>{style_block}</head>
#     <body>{text_body}</body>
#     </html>
#     """

#     # Parse FAQ section into questions and answers
#     faq, ans = extract_faq_sections(faq_html)

#     return {
#         "head": head_html,
#         "slug": slug,
#         "title": title,
#         "text": text_html,
#         "faq": faq,
#         "ans": ans
#     }

# def extract_faq_sections(faq_html):
#     soup = BeautifulSoup(faq_html, 'html.parser')
#     faq = {}
#     ans = {}
#     faq_counter = 1
#     ans_counter = 1

#     tags = soup.find_all(True)

#     for tag in tags:
#         text = tag.get_text(strip=True)
#         if not text:
#             continue

#         # Remove underline from <a> tags inside this tag
#         for a_tag in tag.find_all('a'):
#             current_style = a_tag.get('style', '')
#             if 'text-decoration' not in current_style:
#                 current_style += '; text-decoration: none;'
#             a_tag['style'] = current_style

#         if text.endswith('?'):
#             faq[f'faq-{faq_counter}'] = str(tag)
#             faq_counter += 1
#         else:
#             ans[f'ans-{ans_counter}'] = str(tag)
#             ans_counter += 1

#     return faq, ans

# @app.route('/parse-html', methods=['POST'])
# def parse_html():
#     try:
#         html = request.form.get('html')
#         if not html:
#             return jsonify({'error': 'Missing HTML field'}), 400

#         result = extract_sections_from_html(html)
#         return jsonify(result)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)


from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import re
from bs4 import Tag

app = Flask(__name__)
CORS(app)

def extract_sections_from_html(html):
    sections = html.split('#####')
    sections = [s.strip() for s in sections]

    head_html = sections[0] if len(sections) > 0 else ''
    slug = sections[1] if len(sections) > 1 else ''
    title = sections[2] if len(sections) > 2 else ''
    text_body = sections[3] if len(sections) > 3 else ''
    faq_html = sections[4] if len(sections) > 4 else ''

    # Extract styles from full HTML
    full_soup = BeautifulSoup(html, 'html.parser')
    styles = full_soup.find_all('style')
    style_block = ''.join(str(style) for style in styles)

    # ✅ Process <a> tags in text
    soup_body = BeautifulSoup(text_body, 'html.parser')
    for tag in soup_body.find_all(True):
            if isinstance(tag, Tag) and tag.name == 'a':
                current_style = tag.get('style') or ''
                if 'text-decoration' not in current_style:
                    current_style += '; text-decoration: none;'
                tag['style'] = current_style
    text_body = str(soup_body)

    # ✅ Wrap full HTML document
    text_html = f"""
    <!DOCTYPE html>
    <html>
    <head>{style_block}</head>
    <body>{text_body}</body>
    </html>
    """

    # ✅ Parse FAQ and answers into grouped dicts
    faq_dict, ans_dict = parse_faq_with_separator(faq_html)

    # ✅ Final response
    return {
        "head": head_html,
        "slug": slug,
        "title": title,
        "text": text_html,
        "faq": faq_dict,
        "ans": ans_dict
    }


def parse_faq_with_separator(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Separate by !!!!! as delimiter
    raw_chunks = html.split('!!!!!')
    chunks = [chunk.strip() for chunk in raw_chunks if chunk.strip()]

    faq_dict = {}
    ans_dict = {}

    for i, chunk in enumerate(chunks):
        tag_type = 'faq' if i % 2 == 0 else 'ans'
        index = (i // 2) + 1
        key = f'{tag_type}-{index}'

        cleaned = BeautifulSoup(chunk, 'html.parser')
        for a_tag in cleaned.find_all('a'):
            # current_style = a_tag.get('style', '')
            # if 'text-decoration' not in current_style:
            #     current_style += '; text-decoration: none;'
            # a_tag['style'] = current_style
            if isinstance(a_tag, Tag) and a_tag.name == 'a':
                current_style = a_tag.get('style') or ''
                if 'text-decoration' not in current_style:
                    current_style += '; text-decoration: none;'
                a_tag['style'] = current_style


        if tag_type == 'faq':
            faq_dict[key] = str(cleaned)
        else:
            ans_dict[key] = str(cleaned)

    return faq_dict, ans_dict


@app.route('/parse-html', methods=['POST'])
def parse_html():
    try:
        html = request.form.get('html')
        if not html:
            return jsonify({'error': 'Missing HTML field'}), 400

        print("📥 Received HTML:", html[:300])

        result = extract_sections_from_html(html)
        return jsonify(result)

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)




