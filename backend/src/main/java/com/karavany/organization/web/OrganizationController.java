package com.karavany.organization.web;

import com.karavany.organization.domain.AppUser;
import com.karavany.organization.domain.Organization;
import com.karavany.organization.service.OrganizationService;
import com.karavany.organization.service.OrganizationService.CreateOrganizationCommand;
import com.karavany.organization.service.OrganizationService.FirstDispatcherCommand;
import com.karavany.organization.service.OrganizationService.OrganizationProvisioning;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/organizations")
public class OrganizationController {

    private final OrganizationService service;

    public OrganizationController(OrganizationService service) {
        this.service = service;
    }

    @GetMapping
    @Transactional(readOnly = true)
    public List<OrganizationResponse> list() {
        return service.findAll().stream()
                .map(OrganizationResponse::from)
                .toList();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Transactional
    public OrganizationResponse create(@RequestBody CreateOrganization body) {
        OrganizationProvisioning created = service.create(new CreateOrganizationCommand(
                body.name(), body.subscriptionTier(), body.legalAddress(),
                body.primaryContact(), body.contactChannel(), body.region(),
                body.firstDispatcher() == null ? null : new FirstDispatcherCommand(
                        body.firstDispatcher().fullName(),
                        body.firstDispatcher().login(),
                        body.firstDispatcher().initialPassword(),
                        body.firstDispatcher().contactChannel()
                )
        ));
        return OrganizationResponse.from(created);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleBadRequest(IllegalArgumentException e) {
        return new ErrorResponse(e.getMessage());
    }

    @ExceptionHandler(DataIntegrityViolationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleConflict() {
        return new ErrorResponse("Название организации или логин уже заняты");
    }

    public record CreateOrganization(String name, String subscriptionTier,
                                     String legalAddress, String primaryContact,
                                     String contactChannel, String region,
                                     FirstDispatcher firstDispatcher) {
    }

    public record FirstDispatcher(String fullName, String login,
                                  String initialPassword, String contactChannel) {
    }

    public record OrganizationResponse(UUID id, String tenantKey, String name,
                                       String subscriptionTier, String legalAddress,
                                       String primaryContact, String contactChannel,
                                       String region, String status, OffsetDateTime createdAt,
                                       int userCount, UserResponse firstDispatcher) {
        static OrganizationResponse from(OrganizationProvisioning result) {
            Organization o = result.organization();
            return new OrganizationResponse(o.getId(), o.getTenantKey(), o.getName(),
                    o.getSubscriptionTier(), o.getLegalAddress(), o.getPrimaryContact(),
                    o.getContactChannel(), o.getRegion(), o.getStatus(), o.getCreatedAt(),
                    result.userCount(), result.firstDispatcher() == null
                    ? null : UserResponse.from(result.firstDispatcher()));
        }
    }

    public record UserResponse(UUID id, String fullName, String login,
                               String role, String contactChannel, boolean active,
                               OffsetDateTime createdAt) {
        static UserResponse from(AppUser u) {
            return new UserResponse(u.getId(), u.getFullName(), u.getLogin(),
                    u.getRole(), u.getContactChannel(), u.isActive(), u.getCreatedAt());
        }
    }

    public record ErrorResponse(String message) {
    }
}
