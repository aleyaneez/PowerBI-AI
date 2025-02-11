const COMPANY_NAME_MAP: Record<string, string> = {
    "abastible_consolidado": "abastible",
};

export function getCompanyDisplayName(companyKey: string): string {
    return COMPANY_NAME_MAP[companyKey] || companyKey;
}