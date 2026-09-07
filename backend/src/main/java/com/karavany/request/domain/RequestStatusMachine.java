package com.karavany.request.domain;

import java.util.Collections;
import java.util.EnumSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

public final class RequestStatusMachine {

    public record Transition(RequestStatus from, RequestStatus to, String action,
                             Set<ActorRole> roles, boolean reasonRequired) {
    }

    private static final Set<ActorRole> DISPATCHER = roles(ActorRole.DISPATCHER);
    private static final Set<ActorRole> MASTER = roles(ActorRole.CARAVAN_MASTER);
    private static final Set<ActorRole> DISPATCHER_OR_MASTER =
            roles(ActorRole.DISPATCHER, ActorRole.CARAVAN_MASTER);
    private static final Set<ActorRole> ANY_WITH_SYSTEM =
            roles(ActorRole.DISPATCHER, ActorRole.CARAVAN_MASTER, ActorRole.SYSTEM);

    private static Set<ActorRole> roles(ActorRole... values) {
        return Collections.unmodifiableSet(EnumSet.copyOf(List.of(values)));
    }

    private static final List<Transition> TRANSITIONS = List.of(
            new Transition(RequestStatus.DRAFT, RequestStatus.READY,
                    "Укомплектовать рейс", DISPATCHER, false),
            new Transition(RequestStatus.DRAFT, RequestStatus.CANCELLED,
                    "Отменить заявку", DISPATCHER, false),
            new Transition(RequestStatus.READY, RequestStatus.CANCELLED,
                    "Отменить рейс до выхода", DISPATCHER, false),
            new Transition(RequestStatus.READY, RequestStatus.EN_ROUTE,
                    "Караван вышел на маршрут", MASTER, false),
            new Transition(RequestStatus.EN_ROUTE, RequestStatus.DELAYED,
                    "Зафиксировать задержку", ANY_WITH_SYSTEM, true),
            new Transition(RequestStatus.DELAYED, RequestStatus.EN_ROUTE,
                    "Движение возобновлено", DISPATCHER_OR_MASTER, false),
            new Transition(RequestStatus.EN_ROUTE, RequestStatus.DELIVERED,
                    "Груз доставлен", MASTER, false),
            new Transition(RequestStatus.DELIVERED, RequestStatus.CLOSED,
                    "Закрыть рейс", DISPATCHER, false)
    );

    private RequestStatusMachine() {
    }

    public static List<Transition> all() {
        return TRANSITIONS;
    }

    public static List<Transition> from(RequestStatus status) {
        return TRANSITIONS.stream().filter(t -> t.from() == status).toList();
    }

    public static Optional<Transition> find(RequestStatus from, RequestStatus to) {
        return TRANSITIONS.stream().filter(t -> t.from() == from && t.to() == to).findFirst();
    }

    public static boolean isTerminal(RequestStatus status) {
        return from(status).isEmpty();
    }
}
