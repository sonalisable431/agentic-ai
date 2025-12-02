export interface IValidator {
    performCheck(records: any, warnings: string[], errors: string[]): Promise<boolean>;
}