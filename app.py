# import validators,streamlit as st
# from langchain.prompts import PromptTemplate
# from langchain_groq import ChatGroq
# from langchain.chains.summarize import load_summarize_chain
# from langchain_community.document_loaders import YoutubeLoader,UnstructuredURLLoader


# ## sstreamlit APP
# st.set_page_config(page_title="LangChain: Summarize Text From YT or Website", page_icon="🦜")
# st.title("🦜 LangChain: Summarize Text From YT or Website")
# st.subheader('Summarize URL')



# ## Get the Groq API Key and url(YT or website)to be summarized
# with st.sidebar:
#     groq_api_key=st.text_input("Groq API Key",value="",type="password")

# generic_url=st.text_input("URL",label_visibility="collapsed")

# ## Gemma Model USsing Groq API
# llm =ChatGroq(model="Gemma-7b-It", groq_api_key=groq_api_key)

# prompt_template="""
# Provide a summary of the following content in 300 words:
# Content:{text}

# """
# prompt=PromptTemplate(template=prompt_template,input_variables=["text"])

# if st.button("Summarize the Content from YT or Website"):
#     ## Validate all the inputs
#     if not groq_api_key.strip() or not generic_url.strip():
#         st.error("Please provide the information to get started")
#     elif not validators.url(generic_url):
#         st.error("Please enter a valid Url. It can may be a YT video utl or website url")

#     else:
#         try:
#             with st.spinner("Waiting..."):
#                 ## loading the website or yt video data
#                 if "youtube.com" in generic_url:
#                     loader=YoutubeLoader.from_youtube_url(generic_url,add_video_info=True)
#                 else:
#                     loader=UnstructuredURLLoader(urls=[generic_url],ssl_verify=False,
#                                                  headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
#                 docs=loader.load()

#                 ## Chain For Summarization
#                 chain=load_summarize_chain(llm,chain_type="stuff",prompt=prompt)
#                 output_summary=chain.run(docs)

#                 st.success(output_summary)
#         except Exception as e:
#             st.exception(f"Exception:{e}")


import validators
import streamlit as st
import ssl
import os
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader

# Fix SSL certificate issue for Windows
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

## Streamlit APP
st.set_page_config(page_title="LangChain: Summarize Text From YT or Website", page_icon="🦜")
st.title("🦜 LangChain: Summarize Text From YT or Website")
st.subheader('Summarize URL')

## Get the Groq API Key and url(YT or website) to be summarized
with st.sidebar:
    groq_api_key = st.text_input("Groq API Key", value="", type="password")

generic_url = st.text_input("URL", label_visibility="collapsed", placeholder="Enter YouTube or Website URL")

prompt_template = """
Provide a summary of the following content in 300 words:
Content: {text}
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

if st.button("Summarize the Content from YT or Website"):
    ## Validate all the inputs
    if not groq_api_key.strip():
        st.error("Please provide your Groq API Key")
    elif not generic_url.strip():
        st.error("Please provide a URL to summarize")
    elif not validators.url(generic_url):
        st.error("Please enter a valid URL. It can be a YouTube video URL or website URL")
    else:
        try:
            with st.spinner("Initializing AI model..."):
                ## Initialize Model using Groq API - MOVED INSIDE THE BUTTON CLICK
                llm = ChatGroq(
                    model="llama-3.1-8b-instant",  # Current recommended model
                    groq_api_key=groq_api_key,
                    temperature=0.3
                )
            
            with st.spinner("Loading content..."):
                ## Loading the website or YT video data
                if "youtube.com" in generic_url or "youtu.be" in generic_url:
                    try:
                        # Try multiple approaches for YouTube
                        loader = YoutubeLoader.from_youtube_url(
                            generic_url, 
                            add_video_info=False,  # Changed to False to avoid extra API calls
                            language=["en", "en-US"]
                        )
                        docs = loader.load()
                    except Exception as yt_error:
                        st.error(f"YouTube loading failed: {str(yt_error)}")
                        st.info(" Try these solutions:")
                        st.info("• Make sure the video is public and has captions/transcript")
                        st.info("• Check if the URL is correct")
                        st.info("• Some videos may not have transcripts available")
                        st.stop()
                else:
                    try:
                        loader = UnstructuredURLLoader(
                            urls=[generic_url],
                            ssl_verify=False,
                            headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                            }
                        )
                        docs = loader.load()
                    except Exception as url_error:
                        st.error(f"Website loading failed: {str(url_error)}")
                        st.info(" The website might be blocking automated access or require login")
                        st.stop()
                
                if not docs:
                    st.error("No content could be extracted from the provided URL")
                    st.stop()

            with st.spinner("Generating summary..."):
                ## Chain for Summarization
                chain = load_summarize_chain(
                    llm, 
                    chain_type="stuff", 
                    prompt=prompt
                )
                output_summary = chain.run(docs)

                st.success("Summary generated successfully!")
                st.write("### Summary:")
                st.write(output_summary)
                
        except Exception as e:
            error_msg = str(e).lower()
            st.error(f"An error occurred: {str(e)}")
            
            # More specific error messages
            if "api_key" in error_msg:
                st.info(" Make sure your Groq API Key is correct. Get it from: https://console.groq.com/")
            elif "400" in error_msg or "bad request" in error_msg:
                st.info("YouTube Error Solutions:")
                st.info("• The video might not have captions/transcript available")
                st.info("• Try a different YouTube video with captions")
                st.info("• Make sure the video is public and accessible")
                st.info("• Some YouTube videos block automated transcript access")
            elif "ssl" in error_msg or "certificate" in error_msg:
                st.info("SSL Certificate issue detected. Try running the app again.")
            elif "youtube" in error_msg:
                st.info(" YouTube specific issue:")
                st.info("• Video might be private or deleted")
                st.info("• No transcript/captions available for this video")
                st.info("• Try with a different YouTube video")
            else:
                st.info(" General troubleshooting:")
                st.info("• Check your internet connection")
                st.info("• Try a different URL")
                st.info("• Make sure the content is publicly accessible")

# Add instructions in sidebar
with st.sidebar:
    st.markdown("### Supported Models:")
    st.markdown("• `llama-3.1-8b-instant` (Fast & Current)")
    st.markdown("• `llama-3.3-70b-versatile` (More powerful)")
    st.markdown("• `mixtral-8x7b-32768` (Good balance)")
    st.markdown("• `gemma2-9b-it` (Google's model)")
    st.markdown("---")
    st.markdown("### How to use:")
    st.markdown("1. Get your Groq API key from [console.groq.com](https://console.groq.com/)")
    st.markdown("2. Enter the API key above")
    st.markdown("3. Paste a YouTube or website URL")
    st.markdown("4. Click 'Summarize' button")
    st.markdown("---")
    st.markdown("### Supported URLs:")
    st.markdown("✅ YouTube videos")
    st.markdown("✅ News websites")
    st.markdown("✅ Blogs and articles")
    st.markdown("✅ Most public web pages")