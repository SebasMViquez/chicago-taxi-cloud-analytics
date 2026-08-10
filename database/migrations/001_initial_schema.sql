CREATE TABLE dbo.AnalyticsRuns
(
    AnalyticsRunId BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_AnalyticsRuns PRIMARY KEY,
    SourceDatasetName NVARCHAR(128) NOT NULL,
    SourcePeriodStartDate DATE NULL,
    SourcePeriodEndDate DATE NULL,
    Status NVARCHAR(32) NOT NULL,
    StartedAtUtc DATETIME2(0) NOT NULL CONSTRAINT DF_AnalyticsRuns_StartedAtUtc DEFAULT SYSUTCDATETIME(),
    CompletedAtUtc DATETIME2(0) NULL,
    Notes NVARCHAR(1000) NULL
);
GO

CREATE TABLE dbo.TripDemandByHour
(
    AnalyticsRunId BIGINT NOT NULL,
    DayOfWeek TINYINT NOT NULL,
    HourOfDay TINYINT NOT NULL,
    TripCount BIGINT NOT NULL,
    CreatedAtUtc DATETIME2(0) NOT NULL CONSTRAINT DF_TripDemandByHour_CreatedAtUtc DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_TripDemandByHour PRIMARY KEY (AnalyticsRunId, DayOfWeek, HourOfDay),
    CONSTRAINT FK_TripDemandByHour_AnalyticsRuns FOREIGN KEY (AnalyticsRunId) REFERENCES dbo.AnalyticsRuns(AnalyticsRunId),
    CONSTRAINT CK_TripDemandByHour_DayOfWeek CHECK (DayOfWeek BETWEEN 1 AND 7),
    CONSTRAINT CK_TripDemandByHour_HourOfDay CHECK (HourOfDay BETWEEN 0 AND 23)
);
GO

CREATE TABLE dbo.TripDemandByDay
(
    AnalyticsRunId BIGINT NOT NULL,
    TripDate DATE NOT NULL,
    TripCount BIGINT NOT NULL,
    CreatedAtUtc DATETIME2(0) NOT NULL CONSTRAINT DF_TripDemandByDay_CreatedAtUtc DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_TripDemandByDay PRIMARY KEY (AnalyticsRunId, TripDate),
    CONSTRAINT FK_TripDemandByDay_AnalyticsRuns FOREIGN KEY (AnalyticsRunId) REFERENCES dbo.AnalyticsRuns(AnalyticsRunId)
);
GO

CREATE TABLE dbo.TripDemandByPickupArea
(
    AnalyticsRunId BIGINT NOT NULL,
    PickupCommunityArea INT NOT NULL,
    TripCount BIGINT NOT NULL,
    AverageFare DECIMAL(12,2) NULL,
    AverageTripMiles DECIMAL(10,2) NULL,
    CreatedAtUtc DATETIME2(0) NOT NULL CONSTRAINT DF_TripDemandByPickupArea_CreatedAtUtc DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_TripDemandByPickupArea PRIMARY KEY (AnalyticsRunId, PickupCommunityArea),
    CONSTRAINT FK_TripDemandByPickupArea_AnalyticsRuns FOREIGN KEY (AnalyticsRunId) REFERENCES dbo.AnalyticsRuns(AnalyticsRunId)
);
GO

CREATE TABLE dbo.TripCostByDistanceRange
(
    AnalyticsRunId BIGINT NOT NULL,
    DistanceRangeMiles NVARCHAR(32) NOT NULL,
    TripCount BIGINT NOT NULL,
    AverageFare DECIMAL(12,2) NULL,
    AverageTripTotal DECIMAL(12,2) NULL,
    AverageDurationMinutes DECIMAL(10,2) NULL,
    CreatedAtUtc DATETIME2(0) NOT NULL CONSTRAINT DF_TripCostByDistanceRange_CreatedAtUtc DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_TripCostByDistanceRange PRIMARY KEY (AnalyticsRunId, DistanceRangeMiles),
    CONSTRAINT FK_TripCostByDistanceRange_AnalyticsRuns FOREIGN KEY (AnalyticsRunId) REFERENCES dbo.AnalyticsRuns(AnalyticsRunId)
);
GO

CREATE TABLE dbo.PaymentTypeSummary
(
    AnalyticsRunId BIGINT NOT NULL,
    PaymentType NVARCHAR(64) NOT NULL,
    TripCount BIGINT NOT NULL,
    TotalAmount DECIMAL(18,2) NULL,
    AverageTipPercentage DECIMAL(8,4) NULL,
    CreatedAtUtc DATETIME2(0) NOT NULL CONSTRAINT DF_PaymentTypeSummary_CreatedAtUtc DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_PaymentTypeSummary PRIMARY KEY (AnalyticsRunId, PaymentType),
    CONSTRAINT FK_PaymentTypeSummary_AnalyticsRuns FOREIGN KEY (AnalyticsRunId) REFERENCES dbo.AnalyticsRuns(AnalyticsRunId)
);
GO

CREATE TABLE dbo.MonthlyTripTrend
(
    AnalyticsRunId BIGINT NOT NULL,
    TripYear SMALLINT NOT NULL,
    TripMonth TINYINT NOT NULL,
    TripCount BIGINT NOT NULL,
    AverageFare DECIMAL(12,2) NULL,
    AverageTripMiles DECIMAL(10,2) NULL,
    CreatedAtUtc DATETIME2(0) NOT NULL CONSTRAINT DF_MonthlyTripTrend_CreatedAtUtc DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_MonthlyTripTrend PRIMARY KEY (AnalyticsRunId, TripYear, TripMonth),
    CONSTRAINT FK_MonthlyTripTrend_AnalyticsRuns FOREIGN KEY (AnalyticsRunId) REFERENCES dbo.AnalyticsRuns(AnalyticsRunId),
    CONSTRAINT CK_MonthlyTripTrend_TripMonth CHECK (TripMonth BETWEEN 1 AND 12)
);
GO

CREATE TABLE dbo.DataQualityMetrics
(
    AnalyticsRunId BIGINT NOT NULL CONSTRAINT PK_DataQualityMetrics PRIMARY KEY,
    SourceRows BIGINT NOT NULL,
    AcceptedRows BIGINT NOT NULL,
    RejectedRows BIGINT NOT NULL,
    NullRequiredFieldRows BIGINT NULL,
    InvalidDurationRows BIGINT NULL,
    InvalidDistanceRows BIGINT NULL,
    InvalidFareRows BIGINT NULL,
    CreatedAtUtc DATETIME2(0) NOT NULL CONSTRAINT DF_DataQualityMetrics_CreatedAtUtc DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_DataQualityMetrics_AnalyticsRuns FOREIGN KEY (AnalyticsRunId) REFERENCES dbo.AnalyticsRuns(AnalyticsRunId)
);
GO

CREATE INDEX IX_AnalyticsRuns_Status_StartedAtUtc
ON dbo.AnalyticsRuns (Status, StartedAtUtc DESC);
GO

