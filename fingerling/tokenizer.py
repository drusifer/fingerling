"""Compatibility shim: the tokenizer lives in the `fingerprint_sampler` package."""

from fingerprint_sampler.tokenizer import *  # noqa: F403
from fingerprint_sampler.tokenizer import _MISSING, _MODIFIERS  # noqa: F401
