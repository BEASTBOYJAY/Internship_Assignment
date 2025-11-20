# Copyright (c) Opendatalab. All rights reserved.
import io
import os
from pathlib import Path

import pypdfium2 as pdfium
from loguru import logger

from miner_u_parser.data.data_reader_writer import FileBasedDataWriter
from miner_u_parser.utils.guess_suffix_or_lang import guess_suffix_by_bytes
from miner_u_parser.utils.pdf_image_tools import images_bytes_to_pdf_bytes

pdf_suffixes = ["pdf"]
image_suffixes = ["png", "jpeg", "jp2", "webp", "gif", "bmp", "jpg"]


def read_fn(path):
    if not isinstance(path, Path):
        path = Path(path)
    with open(str(path), "rb") as input_file:
        file_bytes = input_file.read()
        file_suffix = guess_suffix_by_bytes(file_bytes, path)
        if file_suffix in image_suffixes:
            return images_bytes_to_pdf_bytes(file_bytes)
        elif file_suffix in pdf_suffixes:
            return file_bytes
        else:
            raise Exception(f"Unknown file suffix: {file_suffix}")


def prepare_env(output_dir, pdf_file_name, parse_method):
    local_md_dir = str(os.path.join(output_dir, pdf_file_name, parse_method))
    local_image_dir = os.path.join(str(local_md_dir), "images")
    os.makedirs(local_image_dir, exist_ok=True)
    os.makedirs(local_md_dir, exist_ok=True)
    return local_image_dir, local_md_dir


def convert_pdf_bytes_to_bytes_by_pypdfium2(
    pdf_bytes, start_page_id=0, end_page_id=None
):

    # 从字节数据加载PDF
    pdf = pdfium.PdfDocument(pdf_bytes)

    # 确定结束页
    end_page_id = (
        end_page_id if end_page_id is not None and end_page_id >= 0 else len(pdf) - 1
    )
    if end_page_id > len(pdf) - 1:
        logger.warning("end_page_id is out of range, use pdf_docs length")
        end_page_id = len(pdf) - 1

    # 创建一个新的PDF文档
    output_pdf = pdfium.PdfDocument.new()

    # 选择要导入的页面索引
    page_indices = list(range(start_page_id, end_page_id + 1))

    # 从原PDF导入页面到新PDF
    output_pdf.import_pages(pdf, page_indices)

    # 将新PDF保存到内存缓冲区
    output_buffer = io.BytesIO()
    output_pdf.save(output_buffer)

    # 获取字节数据
    output_bytes = output_buffer.getvalue()

    pdf.close()  # 关闭原PDF文档以释放资源
    output_pdf.close()  # 关闭新PDF文档以释放资源

    return output_bytes


def _prepare_pdf_bytes(pdf_bytes_list, start_page_id, end_page_id):
    """准备处理PDF字节数据"""
    result = []
    for pdf_bytes in pdf_bytes_list:
        new_pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(
            pdf_bytes, start_page_id, end_page_id
        )
        result.append(new_pdf_bytes)
    return result


def _process_output(
    pdf_info,
    pdf_file_name,
    local_md_dir,
    local_image_dir,
    md_writer,
):
    from miner_u_parser.backend.pipeline.pipeline_middle_json_mkcontent import (
        union_make as pipeline_union_make,
    )

    image_dir = str(os.path.basename(local_image_dir))

    md_content_str = pipeline_union_make(pdf_info, image_dir)
    md_writer.write_string(
        f"{pdf_file_name}.md",
        md_content_str,
    )
    logger.info(f"local output dir is {local_md_dir}")


def _process_pipeline(
    output_dir,
    pdf_file_names,
    pdf_bytes_list,
    p_lang_list,
    parse_method,
    p_formula_enable,
    p_table_enable,
):
    """处理pipeline后端逻辑"""
    from miner_u_parser.backend.pipeline.model_json_to_middle_json import (
        result_to_middle_json as pipeline_result_to_middle_json,
    )
    from miner_u_parser.backend.pipeline.pipeline_analyze import (
        doc_analyze as pipeline_doc_analyze,
    )

    infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = (
        pipeline_doc_analyze(
            pdf_bytes_list,
            p_lang_list,
            parse_method=parse_method,
            formula_enable=p_formula_enable,
            table_enable=p_table_enable,
        )
    )

    for idx, model_list in enumerate(infer_results):

        pdf_file_name = pdf_file_names[idx]
        local_image_dir, local_md_dir = prepare_env(
            output_dir, pdf_file_name, parse_method
        )
        image_writer, md_writer = FileBasedDataWriter(
            local_image_dir
        ), FileBasedDataWriter(local_md_dir)

        images_list = all_image_lists[idx]
        pdf_doc = all_pdf_docs[idx]
        _lang = lang_list[idx]
        _ocr_enable = ocr_enabled_list[idx]

        middle_json = pipeline_result_to_middle_json(
            model_list,
            images_list,
            pdf_doc,
            image_writer,
            _lang,
            _ocr_enable,
            p_formula_enable,
        )

        pdf_info = middle_json["pdf_info"]
        _process_output(
            pdf_info,
            pdf_file_name,
            local_md_dir,
            local_image_dir,
            md_writer,
        )


async def aio_do_parse(
    output_dir,
    pdf_file_names: list[str],
    pdf_bytes_list: list[bytes],
    p_lang_list: list[str],
    parse_method="auto",
    formula_enable=True,
    table_enable=True,
    start_page_id=0,
    end_page_id=None,
):
    # 预处理PDF字节数据
    pdf_bytes_list = _prepare_pdf_bytes(pdf_bytes_list, start_page_id, end_page_id)

    _process_pipeline(
        output_dir,
        pdf_file_names,
        pdf_bytes_list,
        p_lang_list,
        parse_method,
        formula_enable,
        table_enable,
    )
