package com.karavany.request;

import com.karavany.request.domain.ActorRole;
import com.karavany.request.domain.CaravanRequest;
import com.karavany.request.domain.RequestStatus;
import com.karavany.request.domain.RequestStatusMachine;
import com.karavany.request.service.RequestReadinessGuard;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class RequestStatusMachineTest {

    @Test
    @DisplayName("Основной поток: Draft → Ready → En Route → Delivered → Closed")
    void mainFlowIsAllowed() {
        assertTrue(RequestStatusMachine.find(RequestStatus.DRAFT, RequestStatus.READY).isPresent());
        assertTrue(RequestStatusMachine.find(RequestStatus.READY, RequestStatus.EN_ROUTE).isPresent());
        assertTrue(RequestStatusMachine.find(RequestStatus.EN_ROUTE, RequestStatus.DELIVERED).isPresent());
        assertTrue(RequestStatusMachine.find(RequestStatus.DELIVERED, RequestStatus.CLOSED).isPresent());
    }

    @Test
    @DisplayName("Задержка и возобновление движения: En Route ↔ Delayed")
    void delayIsReversible() {
        assertTrue(RequestStatusMachine.find(RequestStatus.EN_ROUTE, RequestStatus.DELAYED).isPresent());
        assertTrue(RequestStatusMachine.find(RequestStatus.DELAYED, RequestStatus.EN_ROUTE).isPresent());
    }

    @Test
    @DisplayName("Переходы через этап запрещены: Draft → En Route, Ready → Delivered")
    void skippingStagesIsRejected() {
        assertTrue(RequestStatusMachine.find(RequestStatus.DRAFT, RequestStatus.EN_ROUTE).isEmpty());
        assertTrue(RequestStatusMachine.find(RequestStatus.READY, RequestStatus.DELIVERED).isEmpty());
        assertTrue(RequestStatusMachine.find(RequestStatus.DRAFT, RequestStatus.CLOSED).isEmpty());
    }

    @Test
    @DisplayName("Отмена возможна только до выхода каравана на маршрут")
    void cancellationOnlyBeforeDeparture() {
        assertTrue(RequestStatusMachine.find(RequestStatus.DRAFT, RequestStatus.CANCELLED).isPresent());
        assertTrue(RequestStatusMachine.find(RequestStatus.READY, RequestStatus.CANCELLED).isPresent());
        assertTrue(RequestStatusMachine.find(RequestStatus.EN_ROUTE, RequestStatus.CANCELLED).isEmpty());
        assertTrue(RequestStatusMachine.find(RequestStatus.DELAYED, RequestStatus.CANCELLED).isEmpty());
    }

    @Test
    @DisplayName("Closed и Cancelled — финальные статусы")
    void terminalStatuses() {
        assertTrue(RequestStatusMachine.isTerminal(RequestStatus.CLOSED));
        assertTrue(RequestStatusMachine.isTerminal(RequestStatus.CANCELLED));
        assertFalse(RequestStatusMachine.isTerminal(RequestStatus.DELIVERED));
        assertFalse(RequestStatusMachine.isTerminal(RequestStatus.DRAFT));
    }

    @Test
    @DisplayName("Права ролей: выход на маршрут — караван-мастер, закрытие рейса — диспетчер")
    void rolesAreRestricted() {
        var departure = RequestStatusMachine.find(RequestStatus.READY, RequestStatus.EN_ROUTE).orElseThrow();
        assertTrue(departure.roles().contains(ActorRole.CARAVAN_MASTER));
        assertFalse(departure.roles().contains(ActorRole.DISPATCHER));

        var closing = RequestStatusMachine.find(RequestStatus.DELIVERED, RequestStatus.CLOSED).orElseThrow();
        assertTrue(closing.roles().contains(ActorRole.DISPATCHER));
        assertFalse(closing.roles().contains(ActorRole.CARAVAN_MASTER));

        var delay = RequestStatusMachine.find(RequestStatus.EN_ROUTE, RequestStatus.DELAYED).orElseThrow();
        assertTrue(delay.roles().contains(ActorRole.SYSTEM), "UC-19: инцидент переводит рейс в Delayed");
    }

    @Test
    @DisplayName("Причина обязательна только для фиксации задержки (Vision: «причины задержек»)")
    void reasonIsRequiredOnlyForDelay() {
        assertTrue(RequestStatusMachine.find(RequestStatus.EN_ROUTE, RequestStatus.DELAYED).orElseThrow().reasonRequired());
        assertFalse(RequestStatusMachine.find(RequestStatus.DRAFT, RequestStatus.CANCELLED).orElseThrow().reasonRequired());
        assertFalse(RequestStatusMachine.find(RequestStatus.READY, RequestStatus.CANCELLED).orElseThrow().reasonRequired());
        assertFalse(RequestStatusMachine.find(RequestStatus.DRAFT, RequestStatus.READY).orElseThrow().reasonRequired());
    }

    @Test
    @DisplayName("Возврата из Ready в Draft статусная модель не предусматривает")
    void returnToDraftIsNotInTheModel() {
        assertTrue(RequestStatusMachine.find(RequestStatus.READY, RequestStatus.DRAFT).isEmpty());
    }

    @Test
    @DisplayName("Проверок готовности пока нет: FR-10 требует модели команды рейса из UC-9")
    void noReadinessBlockersUntilTeamModelExists() {
        CaravanRequest request = sampleRequest();
        request.applyRisk(null, "NA", null);
        for (RequestStatus target : RequestStatus.values()) {
            assertNull(RequestReadinessGuard.blockerFor(request, target),
                    "неожиданная блокировка перехода в " + target);
        }
    }

    @Test
    @DisplayName("Каждая пара «статус → статус» описана в модели один раз")
    void transitionTableHasNoDuplicates() {
        long distinct = RequestStatusMachine.all().stream()
                .map(t -> t.from() + "->" + t.to())
                .distinct()
                .count();
        assertEquals(RequestStatusMachine.all().size(), distinct);
    }

    private CaravanRequest sampleRequest() {
        return new CaravanRequest(null, "Goodsprings", "New Vegas", LocalDate.now().plusDays(1),
                "Медикаменты", 3000, null);
    }
}
