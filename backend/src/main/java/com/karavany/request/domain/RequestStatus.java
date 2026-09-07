package com.karavany.request.domain;

public enum RequestStatus {

    DRAFT("Черновик"),
    READY("Готов к отправке"),
    EN_ROUTE("В пути"),
    DELAYED("Задержка"),
    DELIVERED("Доставлен"),
    CLOSED("Закрыт"),
    CANCELLED("Отменён");

    private final String label;

    RequestStatus(String label) {
        this.label = label;
    }

    public String label() {
        return label;
    }

    public static RequestStatus parse(String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("Не указан целевой статус");
        }
        try {
            return valueOf(value.trim().toUpperCase(java.util.Locale.ROOT));
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Неизвестный статус заявки: " + value);
        }
    }
}
