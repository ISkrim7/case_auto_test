#!/usr/bin/env python
# -*- coding:utf-8 -*-
from enum import Enum
from typing import List, Mapping, Any, Dict, Optional, Union
import re
from json import JSONDecodeError
from httpx import Response
from jmespath.exceptions import LexerError
from utils import MyLoguru, JsonExtract
from utils.assertsUtil import MyAsserts
from utils.transform import Transform

log = MyLoguru().get_logger()


class AssertTarget(Enum):
    STATUS_CODE = "status_code"
    RESPONSE_TEXT = "response_text"
    RESPONSE_BODY = "response_body"
    RESPONSE_HEADER = "response_header"


class ExtractMethod(Enum):
    JSONPATH = "jsonpath"
    JMESPATH = "jmespath"
    REGEX = "re"


class ExecAsserts:
    """
    执行断言
    """

    ERROR_RESULT = {
        "actual": None,
        "result": False
    }

    TARGET_HANDLERS = {
        AssertTarget.STATUS_CODE: "assert_status_code",
        AssertTarget.RESPONSE_TEXT: "assert_response_text",
        AssertTarget.RESPONSE_BODY: "assert_response_json",
        AssertTarget.RESPONSE_HEADER: "assert_response_header",
    }

    TARGET_EXTRACT_METHODS = {
        AssertTarget.STATUS_CODE: set(),
        AssertTarget.RESPONSE_TEXT: {ExtractMethod.REGEX},
        AssertTarget.RESPONSE_BODY: {ExtractMethod.JSONPATH, ExtractMethod.JMESPATH},
        AssertTarget.RESPONSE_HEADER: {ExtractMethod.JSONPATH, ExtractMethod.JMESPATH},
    }

    def __init__(self, response: Optional[Response] = None, variables: Optional[Dict] = None):
        self.variables = variables or {}
        self.response = response
        self._transformer = Transform(self.variables)

    async def __call__(self, asserts_info: List[Mapping[str, Any]]) -> List[Dict]:
        """
        Execute all assertions with optimized processing

        Args:
            asserts_info: List of assertion configurations

        Returns:
            List of assertion results with original config plus results
        """
        if not asserts_info:
            return []

        log.debug(f"Executing {len(asserts_info)} assertions")

        # Process only enabled assertions
        enabled_asserts = [a for a in asserts_info if a.get("assert_switch", False)]

        # Execute assertions in parallel (if I/O bound) or sequentially
        results = []
        for assertion in enabled_asserts:
            try:
                result = await self._process_single_assertion(assertion)
                results.append({**assertion, **result})
            except Exception as e:
                log.error(f"Assertion failed: {assertion}, error: {str(e)}")
                results.append({**assertion, **self.ERROR_RESULT})

        return results

    async def _process_single_assertion(self, assertion: Mapping[str, Any]) -> Dict:
        """Process a single assertion with proper validation"""
        assert_target = AssertTarget(assertion["assert_target"])
        assert_extract = ExtractMethod(assertion["assert_extract"])

        # Validate extract method for target
        if assert_extract not in self.TARGET_EXTRACT_METHODS[assert_target]:
            log.error(f"Invalid extract method {assert_extract} for target {assert_target}")
            return self.ERROR_RESULT

        # Get handler method dynamically
        handler_name = self.TARGET_HANDLERS[assert_target]
        handler = getattr(self, handler_name)

        # Transform expected value
        expect_value = await self._transformer.transform_target(assertion["assert_value"])
        log.debug(f"Transformed expect_value: {expect_value}")

        # Execute assertion
        return await handler(
            assert_opt=assertion["assert_opt"],
            assert_value=expect_value,
            assert_text=assertion.get("assert_text"),
            assert_extract=assert_extract
        )

    async def assert_status_code(self, assert_opt: str, assert_value: Any, **_) -> Dict:
        """Assert on response status code"""
        return await self._base_assert(
            assert_opt,
            assert_value,
            self.response.status_code
        )

    async def assert_response_text(self, assert_opt: str, assert_value: Any,
                                   assert_text: str, assert_extract: ExtractMethod, **_) -> Dict:
        """Assert on response text using regex"""
        if not assert_text:
            log.error("Regex pattern required for text assertion")
            return self.ERROR_RESULT

        target = self.response.text
        match = re.search(assert_text, target)
        actual = match.group(1) if match else None
        return await self._base_assert(assert_opt, assert_value, actual)

    async def assert_response_json(self, assert_opt: str, assert_value: Any,
                                   assert_text: str, assert_extract: ExtractMethod, **_) -> Dict:
        """Assert on JSON response body"""
        if not assert_text:
            log.error("Extraction path required for JSON assertion")
            return self.ERROR_RESULT

        try:
            target = self.response.json()
            actual = await self._extract_value(target, assert_text, assert_extract)
            return await self._base_assert(assert_opt, assert_value, actual)
        except JSONDecodeError as e:
            log.error(f"Invalid JSON: {str(e)}")
            return self.ERROR_RESULT

    async def assert_response_header(self, assert_opt: str, assert_value: Any,
                                     assert_text: str, assert_extract: ExtractMethod, **_) -> Dict:
        """Assert on response headers"""
        if not assert_text:
            log.error("Extraction path required for header assertion")
            return self.ERROR_RESULT

        target = dict(self.response.headers)
        actual = await self._extract_value(target, assert_text, assert_extract)
        return await self._base_assert(assert_opt, assert_value, actual)

    async def _extract_value(self, target: Any, path: str, method: ExtractMethod) -> Any:
        """Extract value from target using specified method"""
        try:
            if method == ExtractMethod.JSONPATH:
                return await self._json_extractor.value(target, path)
            elif method == ExtractMethod.JMESPATH:
                return self._json_extractor.search(target, path)
        except (LexerError, JSONDecodeError) as e:
            log.error(f"Extraction failed: {str(e)}")
            return None

    async def _base_assert(self, operator: str, expected: Any, actual: Any) -> Dict:
        """Base assertion method with standardized result format"""
        result = {
            "actual": actual,
            "result": False
        }

        if actual is None:
            return result

        try:
            MyAsserts.option(operator, expected, actual)
            result["result"] = True
        except AssertionError as e:
            log.debug(f"Assertion failed: {str(e)}")

        return result
