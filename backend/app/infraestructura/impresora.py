"""Impresora – spool de impresión (IPP). Usada por CU028 (listado de orden de mérito) y CU027."""
from ..pendiente import pendiente


class Impresora:
    def imprimir(self, documento: bytes) -> None:
        pendiente("CU028: enviar el listado al spool IPP")
