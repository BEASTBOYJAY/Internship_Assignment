import os
import asyncio
from pathlib import Path
from loguru import logger

from miner_u_parser.utils.config_reader import get_device
from miner_u_parser.utils.guess_suffix_or_lang import guess_suffix_by_path
from miner_u_parser.utils.model_utils import get_vram
from .common import aio_do_parse, read_fn, pdf_suffixes, image_suffixes


class PDFConverter:
    def __init__(
        self,
        method="auto",
        lang="en",
        start_page_id=0,
        end_page_id=None,
        formula_enable=True,
        table_enable=True,
        device_mode=None,
        virtual_vram=None,
        **kwargs,
    ):
        """
        Initialize the converter with configuration settings.
        Default values are set here, so you don't need to pass them unless necessary.
        """
        self.method = method
        self.lang = lang
        self.start_page_id = start_page_id
        self.end_page_id = end_page_id
        self.formula_enable = formula_enable
        self.table_enable = table_enable
        self.kwargs = kwargs

        # --- Environment Setup Logic (Preserved from original) ---

        # 1. Configure Device Mode
        if device_mode is None:
            self.device_mode = get_device()
        else:
            self.device_mode = device_mode

        if os.getenv("MINERU_DEVICE_MODE", None) is None:
            os.environ["MINERU_DEVICE_MODE"] = self.device_mode

        # 2. Configure VRAM
        if virtual_vram is not None:
            self.vram = virtual_vram
        elif self.device_mode.startswith("cuda") or self.device_mode.startswith("npu"):
            self.vram = round(get_vram(self.device_mode))
        else:
            self.vram = 1

        if os.getenv("MINERU_VIRTUAL_VRAM_SIZE", None) is None:
            os.environ["MINERU_VIRTUAL_VRAM_SIZE"] = str(self.vram)

    def convert(self, input_path, output_dir):
        """
        The main method to trigger conversion.
        Handles asyncio loop internally so you can call this synchronously.
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Determine list of files to process
        path_obj = Path(input_path)
        doc_path_list = []

        if path_obj.is_dir():
            for doc_path in path_obj.glob("*"):
                if guess_suffix_by_path(doc_path) in pdf_suffixes + image_suffixes:
                    doc_path_list.append(doc_path)
        else:
            doc_path_list.append(path_obj)

        if not doc_path_list:
            logger.warning(f"No valid files found at {input_path}")
            return

        # Run the async process
        asyncio.run(self._process_batch(doc_path_list, output_dir))

    async def _process_batch(self, path_list: list[Path], output_dir):
        """Internal async worker to handle the parsing logic."""
        try:
            file_name_list = []
            pdf_bytes_list = []
            lang_list = []

            for path in path_list:
                file_name = str(Path(path).stem)
                pdf_bytes = read_fn(path)

                file_name_list.append(file_name)
                pdf_bytes_list.append(pdf_bytes)
                lang_list.append(self.lang)

            await aio_do_parse(
                output_dir=output_dir,
                pdf_file_names=file_name_list,
                pdf_bytes_list=pdf_bytes_list,
                p_lang_list=lang_list,
                parse_method=self.method,
                formula_enable=self.formula_enable,
                table_enable=self.table_enable,
                start_page_id=self.start_page_id,
                end_page_id=self.end_page_id,
                **self.kwargs,
            )
            logger.info(
                f"Successfully processed {len(path_list)} files to {output_dir}"
            )

        except Exception as e:
            logger.exception(e)
            print(f"An error occurred: {e}")
