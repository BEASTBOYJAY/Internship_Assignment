import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate


from prompt_templates import (
    SUMMARIZER_TEMPLATE,
    JSON_EXTRACTION_TEMPLATE,
    LESGISLATIVE_CHECK_TEMPLATE,
)
from models import LegislativeAnalysis, ComplianceReport


class MarkdownProcessor:
    def __init__(self, api_key):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", temperature=0.2, google_api_key=api_key
        )

    def load_markdown_file(self, path):
        if not os.path.exists(path):
            print(f"Error: File '{path}' not found.")
            return None

        loader = UnstructuredMarkdownLoader(path)
        docs = loader.load()
        self.markdown_text = "\n".join([doc.page_content for doc in docs])

    def summarize_text(self):
        prompt = PromptTemplate.from_template(SUMMARIZER_TEMPLATE)
        summary_chain = prompt | self.llm | StrOutputParser()
        response = summary_chain.invoke({"context": self.markdown_text})
        return response

    def extract_legislative_data(self):

        parser = PydanticOutputParser(pydantic_object=LegislativeAnalysis)
        prompt = PromptTemplate(
            template=JSON_EXTRACTION_TEMPLATE,
            input_variables=["context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.llm | parser

        try:
            result = chain.invoke({"context": self.markdown_text})
            return result.model_dump()
        except Exception as e:
            print(f"Error during extraction: {e}")
            return None

    def check_legislative_compliance(self):
        parser = PydanticOutputParser(pydantic_object=ComplianceReport)

        prompt = PromptTemplate(
            template=LESGISLATIVE_CHECK_TEMPLATE,
            input_variables=["context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.llm | parser

        try:
            result = chain.invoke({"context": self.markdown_text})
            return result.model_dump()
        except Exception as e:
            print(f"Error during compliance check: {e}")
            return None

    def main(self, path):
        self.load_markdown_file(path)
        summarized_text = self.summarize_text()
        legislative_json = self.extract_legislative_data()
        legislative_check_json = self.check_legislative_compliance()

        return summarized_text, legislative_json, legislative_check_json
