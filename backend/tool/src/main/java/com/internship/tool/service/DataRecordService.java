package com.internship.tool.service;

import com.internship.tool.entity.DataRecord;
import com.internship.tool.entity.dto.DataRecordRequest;
import com.internship.tool.entity.dto.DataRecordResponse;
import com.internship.tool.exception.ResourceNotFoundException;
import com.internship.tool.exception.ValidationException;
import com.internship.tool.repository.DataRecordRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.Caching;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDate;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class DataRecordService {

    private final DataRecordRepository dataRecordRepository;
    private final RestTemplate restTemplate;

    @Value("${ai.service.url:http://localhost:5000}")
    private String aiServiceUrl;

    public Page<DataRecordResponse> getAllRecords(Pageable pageable) {
        return dataRecordRepository
                .findByIsDeletedFalse(pageable)
                .map(this::toResponse);
    }

    @Cacheable(value = "records", key = "#id")
    public DataRecordResponse getRecordById(Long id) {
        DataRecord record = dataRecordRepository
                .findByIdAndIsDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("DataRecord", id));
        return toResponse(record);
    }

    @Transactional
    @CacheEvict(value = {"records", "stats"}, allEntries = true)
    public DataRecordResponse createRecord(DataRecordRequest request) {
        validateRequest(request);

        LocalDate expiryDate = request.getCreatedDate()
                .plusYears(request.getRetentionYears());

        DataRecord record = DataRecord.builder()
                .name(request.getName().trim())
                .description(request.getDescription())
                .dataType(request.getDataType())
                .owner(request.getOwner())
                .department(request.getDepartment())
                .retentionYears(request.getRetentionYears())
                .createdDate(request.getCreatedDate())
                .expiryDate(expiryDate)
                .status("ACTIVE")
                .build();

        DataRecord saved = dataRecordRepository.save(record);
        log.info("Created data record with id: {}", saved.getId());
        return toResponse(saved);
    }

    @Transactional
    @Caching(evict = {
        @CacheEvict(value = "records", key = "#id"),
        @CacheEvict(value = "stats", allEntries = true)
    })
    public DataRecordResponse updateRecord(Long id, DataRecordRequest request) {
        DataRecord record = dataRecordRepository
                .findByIdAndIsDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("DataRecord", id));

        validateRequest(request);

        record.setName(request.getName().trim());
        record.setDescription(request.getDescription());
        record.setDataType(request.getDataType());
        record.setOwner(request.getOwner());
        record.setDepartment(request.getDepartment());
        record.setRetentionYears(request.getRetentionYears());
        record.setCreatedDate(request.getCreatedDate());
        record.setExpiryDate(request.getCreatedDate().plusYears(request.getRetentionYears()));

        DataRecord saved = dataRecordRepository.save(record);
        log.info("Updated data record with id: {}", id);
        return toResponse(saved);
    }

    @Transactional
    @Caching(evict = {
        @CacheEvict(value = "records", key = "#id"),
        @CacheEvict(value = "stats", allEntries = true)
    })
    public void deleteRecord(Long id) {
        DataRecord record = dataRecordRepository
                .findByIdAndIsDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("DataRecord", id));

        // Soft delete — we mark isDeleted = true, never remove from database
        record.setIsDeleted(true);
        record.setStatus("DISPOSED");
        dataRecordRepository.save(record);
        log.info("Soft-deleted data record with id: {}", id);
    }

    @Transactional
    @Caching(evict = {
        @CacheEvict(value = "records", key = "#id"),
        @CacheEvict(value = "stats", allEntries = true)
    })
    public void permanentDelete(Long id) {
        DataRecord record = dataRecordRepository
                .findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("DataRecord", id));
        dataRecordRepository.delete(record);
        log.info("Permanently deleted data record with id: {}", id);
    }

    public Page<DataRecordResponse> searchRecords(String query, Pageable pageable) {
        if (query == null || query.trim().isEmpty()) {
            return getAllRecords(pageable);
        }
        return dataRecordRepository
                .searchByQuery(query.trim(), pageable)
                .map(this::toResponse);
    }

    @Cacheable(value = "stats")
    public Map<String, Long> getStats() {
        long total = dataRecordRepository.countByIsDeletedFalse();
        long active = dataRecordRepository.countByStatusAndIsDeletedFalse("ACTIVE");
        long expiring = dataRecordRepository.countByStatusAndIsDeletedFalse("EXPIRING");
        long disposed = dataRecordRepository.countByIsDeletedTrue();

        return Map.of(
                "total", total,
                "active", active,
                "expiring", expiring,
                "disposed", disposed
        );
    }

    @Transactional
    @Caching(evict = {
        @CacheEvict(value = "records", key = "#id"),
        @CacheEvict(value = "stats", allEntries = true)
    })
    public DataRecordResponse analyzeRecord(Long id) {
        DataRecord record = dataRecordRepository
                .findByIdAndIsDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("DataRecord", id));

        try {
            Map<String, Object> payload = Map.of(
                    "id", record.getId(),
                    "name", record.getName(),
                    "dataType", record.getDataType(),
                    "department", record.getDepartment() != null ? record.getDepartment() : "",
                    "retentionYears", record.getRetentionYears(),
                    "expiryDate", record.getExpiryDate().toString(),
                    "status", record.getStatus()
            );

            @SuppressWarnings("unchecked")
            Map<String, Object> aiResponse = restTemplate.postForObject(
                    aiServiceUrl + "/analyze", payload, Map.class);

            if (aiResponse != null) {
                String aiDescription = (String) aiResponse.get("aiDescription");
                Double aiScore = aiResponse.get("aiScore") instanceof Number
                        ? ((Number) aiResponse.get("aiScore")).doubleValue() : 0.0;
                record.setAiDescription(aiDescription);
                record.setAiScore(aiScore);
                dataRecordRepository.save(record);
                log.info("AI analysis completed for record id: {}", id);
            }
        } catch (Exception e) {
            log.warn("AI service unavailable for record {}: {}", id, e.getMessage());
        }

        return toResponse(dataRecordRepository.findByIdAndIsDeletedFalse(id)
                .orElseThrow(() -> new ResourceNotFoundException("DataRecord", id)));
    }

    @Transactional
    public void updateAiDescription(Long id, String aiDescription, Double aiScore) {
        dataRecordRepository.findByIdAndIsDeletedFalse(id).ifPresent(record -> {
            record.setAiDescription(aiDescription);
            record.setAiScore(aiScore);
            dataRecordRepository.save(record);
        });
    }

    private void validateRequest(DataRecordRequest request) {
        if (request.getName() == null || request.getName().trim().isEmpty()) {
            throw new ValidationException("Name cannot be blank");
        }
        if (request.getRetentionYears() != null && request.getRetentionYears() < 1) {
            throw new ValidationException("Retention period must be at least 1 year");
        }
    }

    // Convert entity to response DTO
    private DataRecordResponse toResponse(DataRecord record) {
        return DataRecordResponse.builder()
                .id(record.getId())
                .name(record.getName())
                .description(record.getDescription())
                .dataType(record.getDataType())
                .owner(record.getOwner())
                .department(record.getDepartment())
                .status(record.getStatus())
                .retentionYears(record.getRetentionYears())
                .createdDate(record.getCreatedDate())
                .expiryDate(record.getExpiryDate())
                .aiDescription(record.getAiDescription())
                .aiScore(record.getAiScore())
                .createdAt(record.getCreatedAt())
                .updatedAt(record.getUpdatedAt())
                .build();
    }
}