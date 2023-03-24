from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import ApplicantForm, create_async_session
from schemas import ApplicantFormSchema, ApplicantFormInDBSchema


class CRUDApplicantForm(object):

    @staticmethod
    @create_async_session
    async def add(applicant_form: ApplicantFormSchema, session: AsyncSession = None) -> ApplicantFormInDBSchema | None:
        applicant_form = ApplicantForm(
            **applicant_form.dict()
        )
        session.add(applicant_form)
        try:
            await session.commit()
        except IntegrityError:
            pass
        else:
            await session.refresh(applicant_form)
            return ApplicantFormInDBSchema(**applicant_form.__dict__)

    @staticmethod
    @create_async_session
    async def delete(applicant_form_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(ApplicantForm)
            .where(ApplicantForm.id == applicant_form_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(applicant_form_id: int = None,
                  user_id: int = None,
                  session: AsyncSession = None) -> ApplicantFormInDBSchema | None:
        if user_id:
            applicant_form = await session.execute(
                select(ApplicantForm)
                .where(ApplicantForm.user_id == user_id)
            )
        else:
            applicant_form = await session.execute(
                select(ApplicantForm)
                .where(ApplicantForm.id == applicant_form_id)
            )
        if applicant_form := applicant_form.first():
            return ApplicantFormInDBSchema(**applicant_form[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(user_id: int = None,
                      is_published: bool = None,
                      session: AsyncSession = None) -> list[ApplicantFormInDBSchema]:
        if user_id:
            applicant_forms = await session.execute(
                select(ApplicantForm)
                .where(ApplicantForm.user_id == user_id)
            )
        elif is_published:
            applicant_forms = await session.execute(
                select(ApplicantForm)
                .where(ApplicantForm.is_published == is_published)
            )
        else:
            applicant_forms = await session.execute(
                select(ApplicantForm)
                .order_by(ApplicantForm.id)
            )
        return [ApplicantFormInDBSchema(**applicant_form[0].__dict__) for applicant_form in applicant_forms]

    @staticmethod
    @create_async_session
    async def update(applicant_form: ApplicantFormInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(ApplicantForm)
            .where(ApplicantForm.id == applicant_form.id)
            .values(**applicant_form.dict())
        )
        await session.commit()
