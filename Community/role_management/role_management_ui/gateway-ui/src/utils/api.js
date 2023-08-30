const callApi = (url, method, data) => {
    const headers = {
        Accept: 'application/json, */*;q=0.5',
    };
    headers['Content-Type'] = 'application/json';
    const content = {
        method,
        headers,
    };
    if (data) content.body = JSON.stringify(data);

    return fetch(url, content);
};

export { callApi };
