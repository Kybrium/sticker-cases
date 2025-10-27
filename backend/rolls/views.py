from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers import RouletteSerializer
from .models import Round, TicketUsage, NFTBet, TonBet, BaseBet
from users.models import CustomUser, UserInventory
from packs.serializers import RequestLiquiditySerializer
from .tasks import finish_round_task
from consumers import WSConsumer
from django.db import transaction
from packs.models import Liquidity
from asgiref.sync import async_to_sync


class UserAPIViewSet(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RouletteSerializer

    @action(detail=False, methods=["POST"], url_path="(?P<telegram_id>[^/.]+)/bet")
    def add_bet(self, request: Request, telegram_id: int | None = None) -> Response:
        serializer = UserSerializer(data={"telegram_id": telegram_id})
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(telegram_id=telegram_id)
        round = Round.objects.filter(is_active=True)
        bets = request.data.get("bets")

        if not round:
            return Response({"status": "error", "message": "Нету доступных раундов для ставки"})

        ticket_used = TicketUsage.objects.filter(user=user)

        if not ticket_used:
            if user.tickets == 0:
                return Response({"status": "error", "message": "У пользователя нету тикетов"})
            user.tickets += 1
            user.save()

        nft_bet = request.POST.get("nft")

        if nft_bet:
            try:
                bets_to_add = []
                with transaction.atomic():

                    for bet_id in bets.values():
                        try:
                            liquidity = Liquidity.objects.get(id=bet_id)
                            UserInventory.objects.get(liquidity=liquidity, user=user)

                            bets_to_add.append(
                                NFTBet(
                                    round=round,
                                    user=user,
                                    liquidity=liquidity,
                                )
                            )
                        except Liquidity.DoesNotExist:
                            return Response(
                                {"status": "error", "message": f"Нету такой ликвидности", "bet_id": bet_id},
                                status=drf_status.HTTP_400_BAD_REQUEST,
                            )
                        except UserInventory.DoesNotExist:
                            return Response(
                                {"status": "error", "message": f"У пользователя нету такой ликвидности",
                                 "bet_id": bet_id},
                                status=drf_status.HTTP_400_BAD_REQUEST,
                            )

                NFTBet.objects.bulk_create(bets_to_add)

            except Exception as e:
                return Response(
                    {"status": "error", "message": f"Ошибка при добавлении ставок: {e}"},
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )

        else:
            ton_amount = request.data.get("bets")
            TonBet.objects.create(user=user, amount=ton_amount, round=round)

        total_players = (
                NFTBet.objects.filter(round=round).count()
                + TonBet.objects.filter(round=round).count()
        )

        if total_players == 2:
            async_to_sync(finish_round_task)(round)

        ws_payload = {"bet": {"user": telegram_id,
                              "nfts" if nft_bet else "ton": bets}}

        # TODO: протестировать отправку данных по вебсокету

        WSConsumer.send_json(ws_payload)

        if ticket_used:
            return Response({"status": "success", "message": "Ставка добавлена в рулетку"}, drf_status.HTTP_200_OK)
        return Response({"status": "success", "message": "Списан билет и ставка добавлена в рулетку"},
                        drf_status.HTTP_200_OK)

    @action(detail=False, methods=["POST"], url_path="(?P<telegram_id>[^/.]+)/winnings")
    def add_winnings(self, request: Request, telegram_id: int | None = None) -> Response:
        pass

    # TODO: сделать админскую вьюху которая будет создавать раунд с которого все и начинается
