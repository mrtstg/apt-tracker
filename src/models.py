from __future__ import annotations
from pydantic import BaseModel
import logging
from typing import Any


class Speciality(BaseModel):
    id: int
    name: str
    education: str
    is_commercial: bool

    @staticmethod
    def read(data: dict) -> Speciality | None:
        try:
            return Speciality(
                id=data["id"],
                education=data["Education"],
                name=data["Name"],
                is_commercial=data["Study"] == "Коммерческая",
            )
        except Exception as e:
            logging.error("Failed to parse Speciality: %s" % str(e))
            return None


class GroupInfo(BaseModel):
    id: int
    study: str
    name: str
    plan: int
    education: str
    students: list[Student]

    def is_budget(self) -> bool:
        return self.study == "Бюджетная"

    @staticmethod
    def read(data: dict) -> GroupInfo | None:
        try:
            return GroupInfo(
                id=data["group"]["id"],
                study=data["group"]["Study"],
                name=data["group"]["Name"],
                plan=data["group"]["Plan"],
                education=data["group"]["Education"],
                students=list(
                    filter(
                        lambda x: x is not None,
                        map(lambda x: Student.read(x), data["out"]),
                    )
                ),  # type: ignore
            )
        except Exception as e:
            logging.error("Failed to parse GroupInfo: %s" % str(e))
            return None


class Student(BaseModel):
    grade: float
    doc_number: str
    benefit: bool = False
    crossed: bool = False

    @staticmethod
    def read(data: list[Any]) -> Student | None:
        try:
            return Student(
                grade=data[2],
                doc_number=data[1],
                benefit=data[0] == 1,
                crossed=data[3] == 1,
            )
        except Exception as e:
            logging.error("Failed to parse Student: %s" % str(e))
            return None
