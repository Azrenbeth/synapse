# Copyright 2014-2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" This module contains base REST classes for constructing REST servlets. """
import logging
from typing import Iterable, List, Mapping, Optional, Sequence, overload

from typing_extensions import Literal

from twisted.web.server import Request

from synapse.api.errors import Codes, SynapseError
from synapse.types import JsonDict
from synapse.util import json_decoder

logger = logging.getLogger(__name__)


@overload
def parse_integer(request: Request, name: str, default: int) -> int:
    ...


@overload
def parse_integer(request: Request, name: str, *, required: Literal[True]) -> int:
    ...


@overload
def parse_integer(
    request: Request, name: str, default: Optional[int] = None, required: bool = False
) -> Optional[int]:
    ...


def parse_integer(
    request: Request, name: str, default: Optional[int] = None, required: bool = False
) -> Optional[int]:
    """Parse an integer parameter from the request string

    Args:
        request: the twisted HTTP request.
        name: the name of the query parameter.
        default: value to use if the parameter is absent, defaults to None.
        required: whether to raise a 400 SynapseError if the parameter is absent,
            defaults to False.

    Returns:
        An int value or the default.

    Raises:
        SynapseError: if the parameter is absent and required, or if the
            parameter is present and not an integer.
    """
    args: Mapping[bytes, Sequence[bytes]] = request.args  # type: ignore
    return parse_integer_from_args(args, name, default, required)


def parse_integer_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[int] = None,
    required: bool = False,
) -> Optional[int]:
    """Parse an integer parameter from the request string

    Args:
        args: A mapping of request args as bytes to a list of bytes (e.g. request.args).
        name: the name of the query parameter.
        default: value to use if the parameter is absent, defaults to None.
        required: whether to raise a 400 SynapseError if the parameter is absent,
            defaults to False.

    Returns:
        An int value or the default.

    Raises:
        SynapseError: if the parameter is absent and required, or if the
            parameter is present and not an integer.
    """
    name_bytes = name.encode("ascii")

    if name_bytes in args:
        try:
            return int(args[name_bytes][0])
        except Exception:
            message = "Query parameter %r must be an integer" % (name,)
            raise SynapseError(400, message, errcode=Codes.INVALID_PARAM)
    else:
        if required:
            message = "Missing integer query parameter %r" % (name,)
            raise SynapseError(400, message, errcode=Codes.MISSING_PARAM)
        else:
            return default


@overload
def parse_boolean(request: Request, name: str, default: bool) -> bool:
    ...


@overload
def parse_boolean(request: Request, name: str, *, required: Literal[True]) -> bool:
    ...


@overload
def parse_boolean(
    request: Request, name: str, default: Optional[bool] = None, required: bool = False
) -> Optional[bool]:
    ...


def parse_boolean(
    request: Request, name: str, default: Optional[bool] = None, required: bool = False
) -> Optional[bool]:
    """Parse a boolean parameter from the request query string

    Args:
        request: the twisted HTTP request.
        name: the name of the query parameter.
        default: value to use if the parameter is absent, defaults to None.
        required: whether to raise a 400 SynapseError if the parameter is absent,
            defaults to False.

    Returns:
        A bool value or the default.

    Raises:
        SynapseError: if the parameter is absent and required, or if the
            parameter is present and not one of "true" or "false".
    """
    args: Mapping[bytes, Sequence[bytes]] = request.args  # type: ignore
    return parse_boolean_from_args(args, name, default, required)


@overload
def parse_boolean_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: bool,
) -> bool:
    ...


@overload
def parse_boolean_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    *,
    required: Literal[True],
) -> bool:
    ...


@overload
def parse_boolean_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[bool] = None,
    required: bool = False,
) -> Optional[bool]:
    ...


def parse_boolean_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[bool] = None,
    required: bool = False,
) -> Optional[bool]:
    """Parse a boolean parameter from the request query string

    Args:
        args: A mapping of request args as bytes to a list of bytes (e.g. request.args).
        name: the name of the query parameter.
        default: value to use if the parameter is absent, defaults to None.
        required: whether to raise a 400 SynapseError if the parameter is absent,
            defaults to False.

    Returns:
        A bool value or the default.

    Raises:
        SynapseError: if the parameter is absent and required, or if the
            parameter is present and not one of "true" or "false".
    """
    name_bytes = name.encode("ascii")

    if name_bytes in args:
        try:
            return {b"true": True, b"false": False}[args[name_bytes][0]]
        except Exception:
            message = (
                "Boolean query parameter %r must be one of ['true', 'false']"
            ) % (name,)
            raise SynapseError(400, message)
    else:
        if required:
            message = "Missing boolean query parameter %r" % (name,)
            raise SynapseError(400, message, errcode=Codes.MISSING_PARAM)
        else:
            return default


@overload
def parse_bytes_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[bytes] = None,
) -> Optional[bytes]:
    ...


@overload
def parse_bytes_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Literal[None] = None,
    *,
    required: Literal[True],
) -> bytes:
    ...


@overload
def parse_bytes_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[bytes] = None,
    required: bool = False,
) -> Optional[bytes]:
    ...


def parse_bytes_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[bytes] = None,
    required: bool = False,
) -> Optional[bytes]:
    """
    Parse a string parameter as bytes from the request query string.

    Args:
        args: A mapping of request args as bytes to a list of bytes (e.g. request.args).
        name: the name of the query parameter.
        default: value to use if the parameter is absent,
            defaults to None. Must be bytes if encoding is None.
        required: whether to raise a 400 SynapseError if the
            parameter is absent, defaults to False.
    Returns:
        Bytes or the default value.

    Raises:
        SynapseError if the parameter is absent and required.
    """
    name_bytes = name.encode("ascii")

    if name_bytes in args:
        return args[name_bytes][0]
    elif required:
        message = "Missing string query parameter %s" % (name,)
        raise SynapseError(400, message, errcode=Codes.MISSING_PARAM)

    return default


@overload
def parse_string(
    request: Request,
    name: str,
    default: str,
    *,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> str:
    ...


@overload
def parse_string(
    request: Request,
    name: str,
    *,
    required: Literal[True],
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> str:
    ...


@overload
def parse_string(
    request: Request,
    name: str,
    *,
    required: bool = False,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> Optional[str]:
    ...


def parse_string(
    request: Request,
    name: str,
    default: Optional[str] = None,
    required: bool = False,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> Optional[str]:
    """
    Parse a string parameter from the request query string.

    If encoding is not None, the content of the query param will be
    decoded to Unicode using the encoding, otherwise it will be encoded

    Args:
        request: the twisted HTTP request.
        name: the name of the query parameter.
        default: value to use if the parameter is absent, defaults to None.
        required: whether to raise a 400 SynapseError if the
            parameter is absent, defaults to False.
        allowed_values: List of allowed values for the
            string, or None if any value is allowed, defaults to None. Must be
            the same type as name, if given.
        encoding: The encoding to decode the string content with.

    Returns:
        A string value or the default.

    Raises:
        SynapseError if the parameter is absent and required, or if the
            parameter is present, must be one of a list of allowed values and
            is not one of those allowed values.
    """
    args: Mapping[bytes, Sequence[bytes]] = request.args  # type: ignore
    return parse_string_from_args(
        args,
        name,
        default,
        required=required,
        allowed_values=allowed_values,
        encoding=encoding,
    )


def _parse_string_value(
    value: bytes,
    allowed_values: Optional[Iterable[str]],
    name: str,
    encoding: str,
) -> str:
    try:
        value_str = value.decode(encoding)
    except ValueError:
        raise SynapseError(400, "Query parameter %r must be %s" % (name, encoding))

    if allowed_values is not None and value_str not in allowed_values:
        message = "Query parameter %r must be one of [%s]" % (
            name,
            ", ".join(repr(v) for v in allowed_values),
        )
        raise SynapseError(400, message)
    else:
        return value_str


@overload
def parse_strings_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    *,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> Optional[List[str]]:
    ...


@overload
def parse_strings_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: List[str],
    *,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> List[str]:
    ...


@overload
def parse_strings_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    *,
    required: Literal[True],
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> List[str]:
    ...


@overload
def parse_strings_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[List[str]] = None,
    *,
    required: bool = False,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> Optional[List[str]]:
    ...


def parse_strings_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[List[str]] = None,
    required: bool = False,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> Optional[List[str]]:
    """
    Parse a string parameter from the request query string list.

    The content of the query param will be decoded to Unicode using the encoding.

    Args:
        args: A mapping of request args as bytes to a list of bytes (e.g. request.args).
        name: the name of the query parameter.
        default: value to use if the parameter is absent, defaults to None.
        required: whether to raise a 400 SynapseError if the
            parameter is absent, defaults to False.
        allowed_values: List of allowed values for the
            string, or None if any value is allowed, defaults to None.
        encoding: The encoding to decode the string content with.

    Returns:
        A string value or the default.

    Raises:
        SynapseError if the parameter is absent and required, or if the
            parameter is present, must be one of a list of allowed values and
            is not one of those allowed values.
    """
    name_bytes = name.encode("ascii")

    if name_bytes in args:
        values = args[name_bytes]

        return [
            _parse_string_value(value, allowed_values, name=name, encoding=encoding)
            for value in values
        ]
    else:
        if required:
            message = "Missing string query parameter %r" % (name,)
            raise SynapseError(400, message, errcode=Codes.MISSING_PARAM)

        return default


@overload
def parse_string_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[str] = None,
    *,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> Optional[str]:
    ...


@overload
def parse_string_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[str] = None,
    *,
    required: Literal[True],
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> str:
    ...


@overload
def parse_string_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[str] = None,
    required: bool = False,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> Optional[str]:
    ...


def parse_string_from_args(
    args: Mapping[bytes, Sequence[bytes]],
    name: str,
    default: Optional[str] = None,
    required: bool = False,
    allowed_values: Optional[Iterable[str]] = None,
    encoding: str = "ascii",
) -> Optional[str]:
    """
    Parse the string parameter from the request query string list
    and return the first result.

    The content of the query param will be decoded to Unicode using the encoding.

    Args:
        args: A mapping of request args as bytes to a list of bytes (e.g. request.args).
        name: the name of the query parameter.
        default: value to use if the parameter is absent, defaults to None.
        required: whether to raise a 400 SynapseError if the
            parameter is absent, defaults to False.
        allowed_values: List of allowed values for the
            string, or None if any value is allowed, defaults to None. Must be
            the same type as name, if given.
        encoding: The encoding to decode the string content with.

    Returns:
        A string value or the default.

    Raises:
        SynapseError if the parameter is absent and required, or if the
            parameter is present, must be one of a list of allowed values and
            is not one of those allowed values.
    """

    strings = parse_strings_from_args(
        args,
        name,
        default=[default] if default is not None else None,
        required=required,
        allowed_values=allowed_values,
        encoding=encoding,
    )

    if strings is None:
        return None

    return strings[0]


def parse_json_value_from_request(
    request: Request, allow_empty_body: bool = False
) -> Optional[JsonDict]:
    """Parse a JSON value from the body of a twisted HTTP request.

    Args:
        request: the twisted HTTP request.
        allow_empty_body: if True, an empty body will be accepted and turned into None

    Returns:
        The JSON value.

    Raises:
        SynapseError if the request body couldn't be decoded as JSON.
    """
    try:
        content_bytes = request.content.read()  # type: ignore
    except Exception:
        raise SynapseError(400, "Error reading JSON content.")

    if not content_bytes and allow_empty_body:
        return None

    try:
        content = json_decoder.decode(content_bytes.decode("utf-8"))
    except Exception as e:
        logger.warning("Unable to parse JSON: %s (%s)", e, content_bytes)
        raise SynapseError(400, "Content not JSON.", errcode=Codes.NOT_JSON)

    return content


def parse_json_object_from_request(
    request: Request, allow_empty_body: bool = False
) -> JsonDict:
    """Parse a JSON object from the body of a twisted HTTP request.

    Args:
        request: the twisted HTTP request.
        allow_empty_body: if True, an empty body will be accepted and turned into
            an empty dict.

    Raises:
        SynapseError if the request body couldn't be decoded as JSON or
            if it wasn't a JSON object.
    """
    content = parse_json_value_from_request(request, allow_empty_body=allow_empty_body)

    if allow_empty_body and content is None:
        return {}

    if not isinstance(content, dict):
        message = "Content must be a JSON object."
        raise SynapseError(400, message, errcode=Codes.BAD_JSON)

    return content


def assert_params_in_dict(body: JsonDict, required: Iterable[str]) -> None:
    absent = []
    for k in required:
        if k not in body:
            absent.append(k)

    if len(absent) > 0:
        raise SynapseError(400, "Missing params: %r" % absent, Codes.MISSING_PARAM)


class RestServlet:

    """A Synapse REST Servlet.

    An implementing class can either provide its own custom 'register' method,
    or use the automatic pattern handling provided by the base class.

    To use this latter, the implementing class instead provides a `PATTERN`
    class attribute containing a pre-compiled regular expression. The automatic
    register method will then use this method to register any of the following
    instance methods associated with the corresponding HTTP method:

      on_GET
      on_PUT
      on_POST
      on_DELETE

    Automatically handles turning CodeMessageExceptions thrown by these methods
    into the appropriate HTTP response.
    """

    def register(self, http_server):
        """Register this servlet with the given HTTP server."""
        patterns = getattr(self, "PATTERNS", None)
        if patterns:
            for method in ("GET", "PUT", "POST", "DELETE"):
                if hasattr(self, "on_%s" % (method,)):
                    servlet_classname = self.__class__.__name__
                    method_handler = getattr(self, "on_%s" % (method,))
                    http_server.register_paths(
                        method, patterns, method_handler, servlet_classname
                    )

        else:
            raise NotImplementedError("RestServlet must register something.")
