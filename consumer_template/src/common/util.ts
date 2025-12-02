//Formatted Error Msg
export function formatedErrorMsg(error: any) {
    return JSON.stringify(error, Object.getOwnPropertyNames(error));
}

