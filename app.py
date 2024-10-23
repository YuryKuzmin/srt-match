import streamlit as st

def parse_srt_timestamps(srt_content):
    """Parse SRT file and extract timestamp blocks with their text."""
    blocks = []
    current_block = {'index': '', 'time': '', 'text': []}
    
    for line in srt_content.strip().split('\n'):
        line = line.strip()
        if not line:
            if current_block['text']:
                blocks.append(current_block.copy())
                current_block = {'index': '', 'time': '', 'text': []}
        elif current_block['index'] == '':
            current_block['index'] = line
        elif current_block['time'] == '':
            current_block['time'] = line
        else:
            current_block['text'].append(line)
    
    if current_block['text']:
        blocks.append(current_block)
    
    return blocks

def split_translation_into_segments(translation_text, num_segments):
    """Split the translation text into roughly equal segments based on punctuation."""
    sentences = []
    current_sentence = []
    
    for word in translation_text.replace('\n', ' ').split():
        current_sentence.append(word)
        if word.endswith(('.', '!', '?', '。', '！', '？')):
            sentences.append(' '.join(current_sentence))
            current_sentence = []
    
    if current_sentence:
        sentences.append(' '.join(current_sentence))
    
    segments = [[] for _ in range(num_segments)]
    current_segment = 0
    
    for sentence in sentences:
        segments[current_segment].append(sentence)
        current_segment = (current_segment + 1) % num_segments
    
    return [' '.join(segment) for segment in segments]

def create_translated_srt(english_srt, translation_text):
    """Create a new SRT file using English timestamps and translated text."""
    blocks = parse_srt_timestamps(english_srt)
    translated_segments = split_translation_into_segments(translation_text, len(blocks))
    
    output_lines = []
    for i, (block, translated_text) in enumerate(zip(blocks, translated_segments)):
        output_lines.extend([
            str(i + 1),
            block['time'],
            translated_text,
            ''
        ])
    
    return '\n'.join(output_lines)

# Streamlit interface
st.title('SRT Translation Helper')
st.write('This tool helps you create a translated SRT file using timestamps from an English SRT file.')

# File upload for English SRT
english_srt_file = st.file_uploader("Upload English SRT file", type=['srt', 'txt'])

# Text area for translated text
translation_text = st.text_area("Paste your translated text here", height=200)

if st.button('Generate Translated SRT'):
    if english_srt_file is not None and translation_text:
        try:
            # Read the English SRT file
            english_srt_content = english_srt_file.getvalue().decode('utf-8')
            
            # Generate the translated SRT
            translated_srt = create_translated_srt(english_srt_content, translation_text)
            
            # Display the result
            st.text_area("Generated SRT", translated_srt, height=300)
            
            # Add download button
            st.download_button(
                label="Download SRT file",
                data=translated_srt.encode('utf-8'),
                file_name="translated.srt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please upload an English SRT file and provide the translated text.")

st.markdown("""
### How to use:
1. Upload your English SRT file
2. Paste your translated text
3. Click 'Generate Translated SRT'
4. Download the generated SRT file

Note: The tool will try to match the translated text to the original timing. Manual adjustments might be needed for perfect timing.
""")
