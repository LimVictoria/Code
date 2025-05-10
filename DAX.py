<MeasureName> = 
VAR AggregatedSecondaryTable = 
    ADDCOLUMNS(
        SUMMARIZE(
            FILTER(
                <SecondaryTable>,
                NOT ISBLANK(<SecondaryTable>[<SecondaryValueField>]) &&
                <SecondaryTable>[<FilterColumn>] IN VALUES(<ReferenceTable>[<ReferenceColumn>]) &&
                <SecondaryTable>[<FilterColumn>] IN { "K1", "K2", "K3" } &&
                <SecondaryTable>[<JoinKey>] = RELATED(<ReferenceTable>[<JoinKeyReference>])
            ),
            <SecondaryTable>[<SecondaryJoinField>]
        ),
        "TotalSecondaryValue",
        CALCULATE(SUM(<SecondaryTable>[<SecondaryValueField>]))
    )

RETURN
SUMX(
    SUMMARIZE(
        FILTER(
            <FactTable>,
            NOT ISBLANK(<FactTable>[<BaseValue>]) &&
            <FactTable>[<FilterKey>] IN VALUES(<ReferenceTable>[<ReferenceKey>]) &&
            <FactTable>[<JoinKey>] = RELATED(<ReferenceTable>[<JoinKeyReference>])
        ),
        <FactTable>[<GroupAttribute1>],
        <FactTable>[<GroupAttribute2>],
        <FactTable>[<GroupAttribute3>],
        <FactTable>[<BaseValue>],
        <FactTable>[<JoinKey>]
    ),
    VAR SelectedOption = SELECTEDVALUE(<SelectionTable>[<SelectionField>], "<DefaultOption>")
    VAR LookupFactor = LOOKUPVALUE(
        <LookupTable>[<LookupValueField>],
        <LookupTable>[<LookupMatchField>], <FactTable>[<JoinKey>]
    )
    VAR AdditionalValue = LOOKUPVALUE(
        AggregatedSecondaryTable[TotalSecondaryValue],
        AggregatedSecondaryTable[<SecondaryJoinField>], <FactTable>[<JoinKey>]
    )
    VAR CombinedValue = <FactTable>[<BaseValue>] + COALESCE(AdditionalValue, 0)

    RETURN
    IF(
        SelectedOption = "<OptionThatAvoidsTransformation>",
        CombinedValue,
        IF(
            ISBLANK(LookupFactor) || LookupFactor = 0,
            0,
            CombinedValue * LookupFactor
        )
    )
)
