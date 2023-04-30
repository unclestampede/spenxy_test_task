from typing import Any, Dict, List

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.db import tables
from app.models import UpdateCardSettings


class CardManipulationService:
    async def update_card(
        self,
        *,
        db: AsyncSession,
        data_in: UpdateCardSettings,
        card_id: str,
        current_users: Dict[str, Any],
    ) -> Any:
        try:
            card = await crud.cards.get_by_id(db=db, card_id=card_id)

            if not card:
                raise HTTPException(status_code=404, detail="Card not found")

            transaction_info = await self._get_transaction_info(db=db, current_users=current_users)

            await self._update_card_nick_name(db=db, data_in=data_in, nick_name=data_in.nick_name, card=card)

            await self._update_card_status(db=db, status=data_in.status, card=card, transaction_info=transaction_info)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Sorry! An error has occurred. Please "
                f"try again later or contact support. Error message is: {str(e)}",
            )

        return card

    async def update_card_status_multiple(
        self, db: AsyncSession, card_id_list: List[str], status: str, current_users: Dict[str, Any]
    ):
        try:
            transaction_info = await self._get_transaction_info(db=db, current_users=current_users)
            for card_id in card_id_list:
                card = await crud.cards.get_by_id(db=db, card_id=card_id)

                await self._update_card_status(
                    db=db,
                    status=status,
                    card=card,
                    transaction_info=transaction_info,
                )
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Sorry! An error has occurred. Please "
                f"try again later or contact support. Error message is: {str(e)}",
            )

    async def _get_transaction_info(self, db: AsyncSession, current_users: Dict[str, Any]) -> models.TransactionInfo:
        accountant = FinanceAccountant(db=db)
        receiver = card.user
        client = current_users.get('client')

        initiator = current_users.get('user')
        if not initiator:
            initiator = crud.user.get(db=db, id=client.superadmin)
        initiator_account = initiator.useraccount

        receiver_account = receiver.useraccount
        if receiver_account:
            receiver_data = f"{receiver_account.first_name} {receiver_account.last_name}, {receiver.email}"
        else:
            receiver_data = f"{receiver.nickname}, {receiver.email}"

        admin_ = await crud.user.get(db=db, id=client.superadmin)
        admin_account = admin_.useraccount

        user_wallet = await get_changed_wallet(db=db, user_=receiver, client=client)
        if not user_wallet:
            raise HTTPException(status_code=400, detail=f"Wallet for user {receiver.email} not found.")

        return models.TransactionInfo(
            accountant=accountant,
            receiver=receiver,
            client=client,
            initiator=initiator,
            initiator_account=initiator_account,
            receiver_account=receiver_account,
            receiver_data=receiver_data,
            admin_=admin_,
            admin_account=admin_account,
            user_wallet=user_wallet,
        )

    async def _update_card_status(
        self, db: AsyncSession, status: str, card: tables.Card, transaction_info: models.TransactionInfo
    ) -> None:
        receiver = card.user
        current_status = card.status

        if status == "CLOSED" and card.status == "CLOSED":
            raise HTTPException(status_code=404, detail=f"Card {card.mask_number} already closed")

        if status == "CLOSED":
            if current_status == "INACTIVE":
                await update_card_counts_by_close_for_freeze(db=db, user_=receiver, client=transaction_info.client)
            else:
                await update_card_counts_by_close(db=db, user_=receiver, client=transaction_info.client)
            await transaction_info.accountant.close_card(
                wallet=[
                    wallet_.wallet for wallet_ in transaction_info.client.wallet if wallet_.wallet.currency == "USD"
                ][0]
                if receiver != transaction_info.initiator
                else transaction_info.user_wallet,
                card=card,
                card_balances=card.balance,
                admin_identifier=f"{transaction_info.admin_account.first_name} {transaction_info.admin_account.last_name}"
                if transaction_info.admin_account
                else transaction_info.admin_.email,
                initiator=f"{transaction_info.initiator_account.first_name} {transaction_info.initiator_account.last_name}, {transaction_info.initiator.email}"
                if transaction_info.initiator_account
                else f"{transaction_info.initiator.nickname}, {transaction_info.initiator.email}",
                receiver=transaction_info.receiver_data if receiver != transaction_info.initiator else None,
                buyer_wallet=transaction_info.user_wallet if receiver != transaction_info.initiator else None,
                for_buyer=True if receiver != transaction_info.initiator else False,
                is_admin_operation=False if transaction_info.initiator.role == UserRole.buyer else True,
            )
        if status == "INACTIVE" and current_status == "ACTIVE":
            await update_card_counts_by_freeze(db=db, user_=receiver, client=transaction_info.client)
        if status == "ACTIVE" and current_status == "INACTIVE":
            await update_card_counts_by_activate(db=db, user_=receiver, client=transaction_info.client)

    async def _update_card_nick_name(
        self,
        db: AsyncSession,
        data_in: UpdateCardSettings,
        nick_name: str,
        card: tables.Card,
    ):
        if nick_name and await check_card_nickname(nick_name):
            raise HTTPException(status_code=400, detail="Bad card`s nick name")

        new_data = data_in.dict()
        new_data['status'] = await updated_card.get('provider_data').get('card_status')
        if not nick_name:
            new_data['nick_name'] = card.nick_name

        card = await crud.cards.update(db=db, db_obj=card, obj_in=CardUpdate(**new_data))
        logger.info(f"UPDATE CARD {card.card_id}, {card.mask_number}")

    async def _update_card_limits(
        self,
        db: AsyncSession,
        data_in: UpdateCardSettings,
        card_id: str,
        card: tables.Card,
        transaction_info: models.TransactionInfo,
    ):
        data_in = await check_update_limits(db=db, card_id=card_id, wallet=user_wallet, data_in=data_in, is_update=True)
        if not data_in:
            raise HTTPException(
                status_code=400,
                detail="The limit cannot exceed 5000 USD or be over ALL TIME limit "
                "or your reserved balance over then total balance",
            )

        if card.balance.limit:
            for limit_ in card.balance.limit:
                if limit_.amount <= 0:
                    raise HTTPException(
                        status_code=400, detail="Invalid limit amount. The amount must be greater than zero."
                    )
                balance = card.balance
                if limit_.interval == LimitType.all_time and limit_.amount <= (balance.used + balance.pending_balance):
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid limit amount. The amount must be greater than sum spend and hold.",
                    )
                if transaction_info.initiator.email in ['crealution.team@gmail.com']:
                    if limit_.interval == LimitType.all_time and limit_.amount < 0.01:
                        raise HTTPException(
                            status_code=400, detail="ALL TIME limit should be over than or equal to $0.01."
                        )
                else:
                    if limit_.interval == LimitType.all_time and limit_.amount < 25:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid limit amount. The amount must be greater than or equal to $25.",
                        )

        provider_name, bin_code = await get_vendor_name(
            db=db, client_id=client.client_id, bin_code=crud.bins.get(db=db, id=card.bin_id).code
        )

        try:
            with ProviderClient(provider_name=provider_name) as provider:
                updated_card = provider.get_response(
                    method_name='update_card', data_in={'data_in': json.loads(data_in.json()), 'card_id': card_id}
                )
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Sorry! The bank is not available now. Please "
                f"try again later or contact support. Error message is: {str(e)}",
            )
        response = await check_response_on_error(data=updated_card)

        if response.status_code != 200:
            raise HTTPException(**response.dict())

        card = await crud.cards.update(db=db, db_obj=card, obj_in=CardUpdate(**new_data))
        logger.info(f"UPDATE CARD {card.card_id}, {card.mask_number}")
        balance = card.balance
        settings = await crud.card_settings.get_by_card(db=db, id=card.id)
        if settings:
            settings = await crud.card_settings.update(
                db=db, db_obj=settings, obj_in=UpdateCardSettings(**data_in.dict())
            )
        if card.balance.limit:
            limits_for_update = [limit.amount for limit in card.balance.limit if limit.interval == LimitType.all_time][
                0
            ]
            add_ba = True if limits_for_update != card.balance.limit else False

            if settings:
                limit = await crud.card_limits.update(
                    db=db, obj_in=[limit for limit in card.balance.limit], settings_id=settings.id
                )
            else:
                limit = max([limit.amount for limit in card.balance.limit]) - balance.limit

            logger.info(
                f'DATA FOR CARD UPDATE: "all time": {add_ba}, "LIMIT AMOUNT": {limit}, "OLD_LIMIT": {balance.limit}'
            )

            if add_ba:
                if limit >= 0:
                    await transaction_info.accountant.topup_card(
                        wallet=[
                            wallet_.wallet
                            for wallet_ in transaction_info.client.wallet
                            if wallet_.wallet.currency == "USD"
                        ][0]
                        if transaction_info.receiver != transaction_info.initiator
                        else transaction_info.user_wallet,
                        card=card,
                        card_balances=card.balance,
                        initiator=f"{transaction_info.initiator_account.first_name} {transaction_info.initiator_account.last_name}, {transaction_info.initiator.email}"
                        if transaction_info.initiator_account
                        else f"{transaction_info.initiator.nickname}, {transaction_info.initiator.email}",
                        amount=abs(limit),
                        admin_identifier=f"{transaction_info.admin_account.first_name} {transaction_info.admin_account.last_name}"
                        if transaction_info.admin_account
                        else transaction_info.admin_.email,
                        receiver=transaction_info.receiver_data
                        if transaction_info.receiver != transaction_info.initiator
                        else None,
                        buyer_wallet=transaction_info.user_wallet
                        if transaction_info.receiver != transaction_info.initiator
                        else None,
                        for_buyer=True if transaction_info.receiver != transaction_info.initiator else False,
                        is_admin_operation=False if transaction_info.initiator.role == UserRole.buyer else True,
                    )
                else:
                    await transaction_info.accountant.withdrawal_card(
                        wallet=[
                            wallet_.wallet
                            for wallet_ in transaction_info.client.wallet
                            if wallet_.wallet.currency == "USD"
                        ][0]
                        if transaction_info.receiver != transaction_info.initiator
                        else transaction_info.user_wallet,
                        card=card,
                        card_balances=card.balance,
                        initiator=f"{transaction_info.initiator_account.first_name} {transaction_info.initiator_account.last_name}, {transaction_info.initiator.email}"
                        if transaction_info.initiator_account
                        else f"{transaction_info.initiator.nickname}, {transaction_info.initiator.email}",
                        amount=abs(limit),
                        admin_identifier=f"{transaction_info.admin_account.first_name} {transaction_info.admin_account.last_name}"
                        if transaction_info.admin_account
                        else transaction_info.admin_.email,
                        receiver=transaction_info.receiver_data
                        if transaction_info.receiver != transaction_info.initiator
                        else None,
                        buyer_wallet=transaction_info.user_wallet
                        if transaction_info.receiver != transaction_info.initiator
                        else None,
                        for_buyer=True if transaction_info.receiver != transaction_info.initiator else False,
                        is_admin_operation=False if transaction_info.initiator.role == UserRole.buyer else True,
                    )
            else:
                limit = [
                    limit.amount
                    for limit in card.balance.limit_per_transaction
                    if limit.interval == LimitType.per_transaction
                ][0]
                await transaction_info.accountant.card_operator.change_per_transaction_limit(
                    balances=card.balance, amount=abs(limit)
                )
                logger.info(f'Change per transaction limit for card {card.mask_number} in {limit} USD')
