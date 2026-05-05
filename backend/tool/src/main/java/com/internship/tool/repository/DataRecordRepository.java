package com.internship.tool.repository;

import com.internship.tool.entity.DataRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface DataRecordRepository extends JpaRepository<DataRecord, Long> {

    // Find all non-deleted records, paginated
    Page<DataRecord> findByIsDeletedFalse(Pageable pageable);

    // Find one non-deleted record by id
    Optional<DataRecord> findByIdAndIsDeletedFalse(Long id);

    // Search by name or description (case-insensitive)
    @Query("SELECT d FROM DataRecord d WHERE d.isDeleted = false AND " +
           "(LOWER(d.name) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(d.description) LIKE LOWER(CONCAT('%', :query, '%')))")
    Page<DataRecord> searchByQuery(@Param("query") String query, Pageable pageable);

    // Find records expiring before a date (for email alerts)
    List<DataRecord> findByExpiryDateBeforeAndIsDeletedFalseAndStatus(
        LocalDate date, String status);

    // Stats: count by status
    long countByStatusAndIsDeletedFalse(String status);

    // Stats: count all active records
    long countByIsDeletedFalse();

    // Stats: count soft-deleted (disposed) records
    long countByIsDeletedTrue();
}