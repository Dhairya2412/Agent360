"""Mock SOPs, product catalog, inventory, and banking policies."""

MOCK_IT_SOPS = [
    {
        "source": "IT-VPN-SOP",
        "content": "VPN issues: verify credentials, reset VPN profile via IT portal, check MFA enrollment. Escalate if outage > 30 min.",
    },
    {
        "source": "IT-MFA-SOP",
        "content": "MFA reset requires identity verification. Use reset_mock_vpn_profile for VPN+MFA bundle reset. Ticket required for hardware tokens.",
    },
    {
        "source": "IT-PASSWORD-SOP",
        "content": "Password resets: verify employee ID, use self-service portal first. Admin reset requires manager approval for privileged accounts.",
    },
    {
        "source": "IT-SOFTWARE-SOP",
        "content": "Software access requests: check license availability, create IT ticket with software SKU and business justification.",
    },
]

MOCK_SUPPLY_POLICIES = [
    {
        "source": "SC-ORDER-POLICY",
        "content": "Orders over 500 units require supply manager approval. Delivery dates must be >= 5 business days out.",
    },
    {
        "source": "SC-INVENTORY-POLICY",
        "content": "Always check inventory before confirming order. Backorder items if stock < requested quantity.",
    },
]

MOCK_BANKING_POLICIES = [
    {
        "source": "BANK-CARD-BLOCK",
        "content": "Blocked card reports: verify last 4 digits, flag account for review if fraud suspected. Never share full PAN.",
    },
    {
        "source": "BANK-DISPUTE",
        "content": "Disputes over $500 require human approval. Document transaction ID, merchant, and customer statement.",
    },
    {
        "source": "BANK-REFUND",
        "content": "Refunds require dual approval for amounts > $1000. Create support case with dispute category.",
    },
]

PRODUCT_CATALOG = {
    "SKU-1001": {"name": "Industrial Bearing 6205", "unit": "each", "price": 12.50},
    "SKU-1002": {"name": "Hydraulic Hose 3/4in", "unit": "meter", "price": 8.75},
    "SKU-1003": {"name": "Safety Gloves (Box of 100)", "unit": "box", "price": 45.00},
    "SKU-1004": {"name": "Steel Bolt M12x50", "unit": "pack", "price": 22.00},
    "SKU-1005": {"name": "Conveyor Belt Segment", "unit": "each", "price": 320.00},
    "SKU-1006": {"name": "Lubricant Oil 5L", "unit": "can", "price": 38.50},
}

INVENTORY = {
    "SKU-1001": 450,
    "SKU-1002": 1200,
    "SKU-1003": 85,
    "SKU-1004": 300,
    "SKU-1005": 12,
    "SKU-1006": 200,
}

def get_mock_sops_for_domain(domain: str) -> list[dict[str, str]]:
    mapping = {
        "IT_HELPDESK": MOCK_IT_SOPS,
        "SUPPLY_CHAIN_ORDER": MOCK_SUPPLY_POLICIES,
        "BANKING_SUPPORT": MOCK_BANKING_POLICIES,
        "GENERAL_ENTERPRISE": MOCK_IT_SOPS + MOCK_SUPPLY_POLICIES,
    }
    return mapping.get(domain, MOCK_IT_SOPS)
