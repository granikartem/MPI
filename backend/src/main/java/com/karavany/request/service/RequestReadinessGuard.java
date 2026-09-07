package com.karavany.request.service;

import com.karavany.request.domain.CaravanRequest;
import com.karavany.request.domain.RequestStatus;

public final class RequestReadinessGuard {

    private RequestReadinessGuard() {
    }

    public static String blockerFor(CaravanRequest request, RequestStatus target) {
        return null;
    }
}
