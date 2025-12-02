export function getProductMapping(data: any) {

    data = typeof data == 'string' ? JSON.parse(data) : data;

    if (data?.stoneNumber) {
        data.stoneNumber = Number(data.stoneNumber);
    }

    if (data?.onlineExclusive) {
        data.onlineExclusive = Boolean(data.onlineExclusive);
    }

    return data;
}