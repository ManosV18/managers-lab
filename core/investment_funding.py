from dataclasses import dataclass
from typing import Sequence

from core.models import CompanyState
from core.investment_company_impact import InvestmentCompanyImpact


@dataclass(frozen=True)
class InvestmentFundingAllocation:
    opening_cash: float
    minimum_cash_reserve: float
    available_internal_cash: float

    total_capex: float
    net_initial_nwc_requirement: float
    working_capital_need: float
    working_capital_source: float

    internal_cash_to_working_capital: float
    internal_cash_to_capex: float

    external_working_capital_required: float
    external_capex_required: float
    total_external_funding_required: float

    cash_reserve_preserved: float


class InvestmentFundingAllocator:
    """Allocate existing cash to investment needs while preserving
    the company's minimum cash reserve.
    """

    @staticmethod
    def allocate(
        state: CompanyState,
        impacts: Sequence[InvestmentCompanyImpact],
    ) -> InvestmentFundingAllocation:

        opening_cash = max(
            0.0, state.drivers.opening_cash
        )
        reserve = max(
            0.0, state.minimum_cash_reserve
        )

        available_cash = max(
            0.0, opening_cash - reserve
        )

        total_capex = sum(
            max(0.0, impact.initial_capex)
            for impact in impacts
        )

        # Net portfolio NWC requirement. A negative value
        # represents a net working-capital source.
        net_nwc = sum(
            impact.initial_nwc_requirement
            for impact in impacts
        )

        wc_need = max(0.0, net_nwc)
        wc_source = max(0.0, -net_nwc)

        # Priority 1: fund incremental working capital.
        cash_to_wc = min(available_cash, wc_need)
        external_wc = wc_need - cash_to_wc

        # Priority 2: use remaining cash, plus any net NWC
        # source, to fund CAPEX.
        remaining_cash = available_cash - cash_to_wc
        cash_for_capex = remaining_cash + wc_source

        cash_to_capex = min(
            cash_for_capex, total_capex
        )
        external_capex = total_capex - cash_to_capex

        return InvestmentFundingAllocation(
            opening_cash=opening_cash,
            minimum_cash_reserve=reserve,
            available_internal_cash=available_cash,
            total_capex=total_capex,
            net_initial_nwc_requirement=net_nwc,
            working_capital_need=wc_need,
            working_capital_source=wc_source,
            internal_cash_to_working_capital=cash_to_wc,
            internal_cash_to_capex=cash_to_capex,
            external_working_capital_required=external_wc,
            external_capex_required=external_capex,
            total_external_funding_required=(
                external_wc + external_capex
            ),
            cash_reserve_preserved=min(opening_cash, reserve),
        )
