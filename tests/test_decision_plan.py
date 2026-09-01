from core.decision import DecisionFactory
from core.decision_plan import DecisionPlan


def main():

    # -------------------------------------------------
    # CREATE DECISIONS
    # -------------------------------------------------

    price = DecisionFactory.price_change(
        decision_id="price_001",
        target_price=160,
    )

    ar = DecisionFactory.ar_days_change(
        decision_id="ar_001",
        target_ar_days=60,
    )

    # -------------------------------------------------
    # CREATE EMPTY PLAN
    # -------------------------------------------------

    plan = DecisionPlan.create(
        plan_id="plan_001",
        name="Test Plan",
    )

    assert plan.is_empty
    assert plan.decision_count == 0

    # -------------------------------------------------
    # ADD
    # -------------------------------------------------

    plan = plan.add(price)

    assert plan.decision_count == 1
    assert plan.contains("price_001")

    # -------------------------------------------------
    # ADD SECOND
    # -------------------------------------------------

    plan = plan.add(ar)

    assert plan.decision_count == 2
    assert plan.contains("price_001")
    assert plan.contains("ar_001")

    # -------------------------------------------------
    # IMMUTABILITY
    # -------------------------------------------------

    assert plan.is_empty is False

    # -------------------------------------------------
    # SUMMARY
    # -------------------------------------------------

    print("\n================ DECISION PLAN ================")

    print(plan.summary())

    print(
        f"Decision Count: {plan.decision_count}"
    )

    # -------------------------------------------------
    # REMOVE
    # -------------------------------------------------

    reduced_plan = plan.remove("ar_001")

    assert reduced_plan.decision_count == 1
    assert reduced_plan.contains("price_001")
    assert not reduced_plan.contains("ar_001")

    # Original plan must remain unchanged
    assert plan.decision_count == 2
    assert plan.contains("ar_001")

    print("\n================ AFTER REMOVE ================")

    print(reduced_plan.summary())

    # -------------------------------------------------
    # DUPLICATE PROTECTION
    # -------------------------------------------------

    try:

        plan.add(price)

        raise AssertionError(
            "Duplicate Decision was not rejected."
        )

    except ValueError:

        pass

    # -------------------------------------------------
    # SUCCESS
    # -------------------------------------------------

    print("\n===============================================")
    print("✅ DECISION PLAN TEST PASSED")
    print("===============================================")


if __name__ == "__main__":
    main()
