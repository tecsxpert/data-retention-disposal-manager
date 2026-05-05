package com.internship.tool.config;

import com.internship.tool.service.AuditLogService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.AfterReturning;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

@Aspect
@Component
@RequiredArgsConstructor
@Slf4j
public class AuditAspect {

    private final AuditLogService auditLogService;

    @AfterReturning(
        pointcut = "execution(* com.internship.tool.service.DataRecordService.createRecord(..))",
        returning = "result"
    )
    public void logCreate(JoinPoint joinPoint, Object result) {
        logAction("CREATE", result);
    }

    @AfterReturning(
        pointcut = "execution(* com.internship.tool.service.DataRecordService.updateRecord(..))",
        returning = "result"
    )
    public void logUpdate(JoinPoint joinPoint, Object result) {
        logAction("UPDATE", result);
    }

    @AfterReturning(
        pointcut = "execution(* com.internship.tool.service.DataRecordService.deleteRecord(..))"
    )
    public void logDelete(JoinPoint joinPoint) {
        String user = getCurrentUser();
        Long id = (Long) joinPoint.getArgs()[0];
        auditLogService.log("DataRecord", id, "DELETE", user, "Record soft-deleted");
    }

    @AfterReturning(
        pointcut = "execution(* com.internship.tool.service.DataRecordService.permanentDelete(..))"
    )
    public void logPermanentDelete(JoinPoint joinPoint) {
        String user = getCurrentUser();
        Long id = (Long) joinPoint.getArgs()[0];
        auditLogService.log("DataRecord", id, "PERMANENT_DELETE", user, "Record permanently deleted");
    }

    private void logAction(String action, Object result) {
        try {
            String user = getCurrentUser();
            var idMethod = result.getClass().getMethod("getId");
            Long id = (Long) idMethod.invoke(result);
            auditLogService.log("DataRecord", id, action, user, action + " performed");
        } catch (Exception e) {
            log.warn("Could not write audit log: {}", e.getMessage());
        }
    }

    private String getCurrentUser() {
        try {
            return SecurityContextHolder.getContext()
                    .getAuthentication().getName();
        } catch (Exception e) {
            return "system";
        }
    }
}
