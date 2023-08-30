import { usePageMessages } from '@bluecat/limani';
import {
    Button,
    Dialog,
    EditorDetailsPanel,
    Layer,
    ModalSpinner,
    TableTitle,
    TableToolbar,
    TableToolbarDefault,
} from '@bluecateng/pelagos';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import AppContext from './AppContext';
import {
    doActionApi,
    getConfigurationsApi,
    getDeploymentOptionApi,
    getRolesApi,
    getViewOptionsApi,
} from './api';
import Confirm from './components/Confirm';
import DeleteRoleConfirm from './components/DeleteRoleConfirm';
import DestinationForm from './components/DestinationForm';
import Filter from './components/Filter';
import ActionResultTable from './components/table/ActionResultTable';
import DeploymentTable from './components/table/DeploymentTable';
import DetailTable from './components/table/DetailTable';
import LazyLoadTable from './components/table/LazyLoadTable';
import { ACTION_NAMES, ROLE_ACTIONS, ZONE_ROLE_ACTIONS } from './constants/action';
import { INHERIT_OPTIONS } from './constants/filter';
import { GROUPBY_OPTIONS, GROUP_TO_COLUMNS } from './constants/group';
import { DEFAULT_COLUMNS, DEFAULT_COLUMNS_WITH_INHERIT, PAGE_SIZE } from './constants/table';
import DropDownField from './pelagos-components/DropDownField';
import { IconMenu, IconMenuItem } from './pelagos-components/menu';
import { getActionPayload, getDeploymentOptionParam } from './processors/common';
import { getDetailData, getIds } from './processors/table';
import './roleManagementPage.less';
import { getSelectedKeys, getTableColumns, preprocessData } from './utils/common';
import { checkDestinationFill } from './utils/form';

function App() {
    const { addErrorMessage } = usePageMessages();

    const lzTableRef = useRef(null);
    const [firstLoadingTable, setFirstLoadingTable] = useState(false);

    const [config, setConfig] = useState(null);
    const [configOptions, setConfigOptions] = useState([]);
    const [view, setView] = useState(null);
    const [viewOptions, setViewOptions] = useState([]);
    const [columns, setColumns] = useState(DEFAULT_COLUMNS);

    const [roles, setRoles] = useState([]);
    const [total, setTotal] = useState(0);
    const [pagination, setPagination] = useState({
        start: 0,
    });

    const [groupBy, setGroupBy] = useState(GROUPBY_OPTIONS[0]);
    const [groupObjSelected, setGroupObjSelected] = useState(null);
    const [groupServerInterfaceId, setGroupServerInterfaceId] = useState(null);

    const [detailData, setDetailData] = useState([]);
    const [deploymentOptionSelected, setDeploymentOptionSelected] = useState(null);
    const [deploymentOptionData, setDeploymentOptionData] = useState(null);
    const [filter, setFilter] = useState({
        server: {},
        svInterface: null,
        interfaceList: [],
        zone: [],
        reverseZone: [],
        group_role: [],
        custom_role: [],
    });

    const [selected, setSelected] = useState({});
    const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
    const [openDeleteResult, setOpenDeleteResult] = useState(false);

    const [selectedDeploymentOption, setSelectedDeploymentOption] = useState();
    const [deploymentDataFromDialog, setDeploymentDataFromDialog] = useState();

    const [selectedAction, setSelectedAction] = useState(null);
    const [destinationFilled, setDestinationFilled] = useState(false);
    const [destination, setDestination] = useState({
        serverInterface: {
            server: {},
            interface: {},
        },

        candidateServer: {},
        candidateSvInterface: {},
        serverInterfaceList: [],

        roleType: null,
        zoneTransferInterface: { server: {}, interface: {} },
        zoneList: [],
        reverseZoneList: [],
    });
    const [handlingValidation, setHandlingValidation] = useState(false);
    const [validationData, setValidationData] = useState(null);
    const [handlingAction, setHandlingAction] = useState(false);
    const [actionResultData, setActionResultData] = useState(null);
    const [containInherited, setContainInherited] = useState(INHERIT_OPTIONS[0]);
    const [deploymentOnDetail, setDeploymentOnDetail] = useState(false);

    const [deploymentData, setDeploymentData] = useState(null);

    const handleClickDetail = useCallback(
        (item) => {
            setGroupObjSelected(item.id);
            setGroupServerInterfaceId(item.serverInterfaceId);
            const detailData = getDetailData(roles, groupBy, item);
            setDetailData(detailData);

            setDeploymentOnDetail(true);

            setDeploymentOptionSelected({
                roleId: detailData[0].id,
                deploymentOptionParam: getDeploymentOptionParam({
                    config,
                    role: detailData[0],
                }),
            });
        },
        [groupBy, roles],
    );

    const hasChecked = () => {
        for (const id of getIds(roles, groupBy)) {
            if (selected[id]) return true;
        }
        return false;
    };

    const requireDestination = useMemo(() => {
        return (
            selectedAction?.name !== ACTION_NAMES.EXPOSE_ROLES &&
            selectedAction?.name !== ACTION_NAMES.HIDE_ROLES &&
            selectedAction?.name !== ACTION_NAMES.DELETE_ROLES
        );
    }, [selectedAction]);

    const showModal = useMemo(() => {
        return (
            selectedAction &&
            !actionResultData &&
            (requireDestination || !handlingValidation) &&
            !openDeleteDialog &&
            !openDeleteResult
        );
    }, [
        selectedAction,
        actionResultData,
        handlingValidation,
        requireDestination,
        openDeleteDialog,
        openDeleteResult,
    ]);

    const showConfirm = useMemo(() => {
        return destinationFilled || handlingAction;
    }, [selectedAction, destinationFilled]);

    const showDestination = useMemo(() => {
        return !destinationFilled && requireDestination && !handlingAction;
    }, [handlingAction, destinationFilled, requireDestination]);

    const rowSelected = (item) => {
        return item.id === groupObjSelected;
    };

    const resetTableStatus = () => {
        setSelected({});
        setGroupObjSelected(null);
        setDetailData([]);
        setDeploymentOptionSelected(null);

        lzTableRef.current.scrollTo(0, 0);

        setTotal(0);
        setRoles([]);

        const newPagination = {
            start: 0,
            end: PAGE_SIZE,
        };
        setPagination(newPagination);
    };

    const handleFilterChange = (value) => {
        resetTableStatus();
        setFilter(value);
    };

    const handleConfigChange = (value) => {
        if (value === config) return;
        resetTableStatus();
        setConfig(value);
        getViewOptions(value);
    };
    const handleViewChange = (value) => {
        if (value === view) return;
        resetTableStatus();
        setView(value);
    };

    const handleGroupChange = (option) => {
        if (option.value === groupBy.value) return;
        resetTableStatus();
        setGroupBy(option);

        setColumns(getTableColumns(option, containInherited));
    };

    const handleChangeInherited = (option) => {
        resetTableStatus();
        setContainInherited(option);

        setColumns(getTableColumns(groupBy, option));
    };

    const getDetailTitle = (groupSelected, groupValue) => {
        return 'Details';
    };

    const detailGroupPanel = groupObjSelected ? (
        <EditorDetailsPanel
            item={{
                id: 'detailGroupPanel',
                name: getDetailTitle(groupObjSelected, groupBy.value),
            }}
            id='detailsPanel'
            showButtons={false}
            onClose={() => {
                setGroupObjSelected(null);
            }}>
            <div>
                <DetailTable
                    title='Roles'
                    data={detailData}
                    groupBy={groupBy}
                    containInherited={containInherited.value}
                    groupObjSelected={groupObjSelected}
                    serverInterfaceId={groupServerInterfaceId}
                    hasMultipleZones={groupBy.value}
                    deploymentOptionSelected={deploymentOptionSelected}
                    onChangeSelected={(newSelected) => setDeploymentOptionSelected(newSelected)}
                />
                <br />
                <DeploymentTable
                    title='DNS Deployment Options'
                    data={deploymentOptionData}
                    containInherited={containInherited.value}
                    onDetail={deploymentOnDetail}
                />
            </div>
        </EditorDetailsPanel>
    ) : undefined;

    const resetDestination = () => {
        setDestination({
            serverInterface: { server: {}, interface: {} },
            candidateServer: {},
            candidateSvInterface: {},
            serverInterfaceList: [],
            roleType: null,
            zoneTransferInterface: { server: {}, interface: {} },
            zoneList: [],
            reverseZoneList: [],
            roleType: '',
            zoneTransfer: '',
        });
    };

    const handleCancel = () => {
        if (!destinationFilled || !requireDestination) {
            setSelectedAction(null);
            resetDestination();
        }
        setDestinationFilled(false);
    };

    const handleCancelDeleteConfirm = () => {
        setOpenDeleteDialog(false);
        setSelectedAction(null);
        setValidationData(null);
        setDestinationFilled(false);
    };

    const handleSubmitError = () => {
        setDestinationFilled(false);
        setSelectedAction(null);
        setValidationData(null);
        setActionResultData(null);
        resetDestination();
        addErrorMessage('Internal Server Error');
    };

    const isDuplicateInterface = useMemo(() => {
        return destination.serverInterfaceList
            .map((s) => s.serverInterface.name)
            .includes(destination.candidateSvInterface?.name);
    }, [
        destination.serverInterfaceList,
        destination.candidateServer,
        destination.candidateSvInterface,
    ]);

    const handleSubmitForm = (action) => {
        const updatedDestination = { ...destination };
        if (updatedDestination.candidateServer.value && updatedDestination.candidateSvInterface) {
            if (
                !isDuplicateInterface &&
                updatedDestination.candidateSvInterface.name !== 'Select Interface'
            )
                updatedDestination.serverInterfaceList = [
                    ...updatedDestination.serverInterfaceList,
                    {
                        server: updatedDestination.candidateServer,
                        serverInterface: updatedDestination.candidateSvInterface,
                    },
                ];

            updatedDestination.candidateServer = {};
            updatedDestination.candidateSvInterface = {};
        }
        setDestination(updatedDestination);

        setHandlingValidation(true);

        const selectedKeys = getSelectedKeys(selected);

        const actionPayload = getActionPayload({
            selectedAction: action || selectedAction,
            groupBy,
            roles,
            selected: selectedKeys,
            destination: updatedDestination,
            view,
            deploymentOptionData,
        });

        doActionApi({
            config,
            selectedAction: action || selectedAction,
            actionPayload,
            validate: true,
        })
            .then((data) => {
                setValidationData(data);
                setDestinationFilled(true);
                setHandlingValidation(false);
            })
            .catch((error) => {
                console.log(error);
                setHandlingValidation(false);
                addErrorMessage('Something went wrong');
                handleSubmitError();
            });
    };

    const handleChoseAction = (action) => {
        if (action.name === ACTION_NAMES.DELETE_ROLES) {
            setDestinationFilled(true);
            handleSubmitForm(action);
            setOpenDeleteDialog(true);
        }
        if (action.name === ACTION_NAMES.EXPOSE_ROLES || action.name === ACTION_NAMES.HIDE_ROLES) {
            setDestinationFilled(true);
            handleSubmitForm(action);
        }
        setSelectedAction(action);
    };

    const handleConfirmAccept = () => {
        setDestinationFilled(false);

        const selectedKeys = getSelectedKeys(selected);
        const selectedOption = getSelectedKeys(selectedDeploymentOption);
        const actionPayload = getActionPayload({
            selectedAction,
            groupBy,
            roles,
            selected: selectedKeys,
            destination,
            view,
            deploymentData: deploymentDataFromDialog,
            optionSelected: selectedOption,
        });

        setHandlingAction(true);
        doActionApi({ config, selectedAction, actionPayload, validate: false })
            .then((data) => {
                setSelected({});
                setGroupObjSelected(null);
                setDetailData([]);
                setDeploymentOptionSelected(null);
                lzTableRef.current.scrollTo(0, 0);

                getRolesApi({
                    config,
                    view,
                    groupBy,
                    containInherited,
                    filter,
                    pagination: { start: 0 },
                })
                    .then((res) => {
                        if (res.total > 0) {
                            setTotal(res.total);
                            setRoles(preprocessData(res.data, groupBy, containInherited));

                            const newPagination = {
                                start: PAGE_SIZE,
                            };
                            setPagination(newPagination);
                            setActionResultData(data);
                            resetDestination();
                        }
                    })
                    .catch((error) => console.log(error))
                    .finally(() => setHandlingAction(false));
            })
            .catch((error) => {
                console.log(error);
                setHandlingAction(false);
                addErrorMessage('Something went wrong');
                handleSubmitError();
            });
    };

    const handleConfirmAcceptDelete = () => {
        const selectedKeys = getSelectedKeys(selected);
        const actionPayload = getActionPayload({
            selectedAction,
            groupBy,
            roles,
            selected: selectedKeys,
            destination,
            view,
        });

        setHandlingAction(true);
        doActionApi({ config, selectedAction, actionPayload, validate: false })
            .then((data) => {
                setGroupObjSelected(null);
                setDetailData([]);
                setDeploymentOptionSelected(null);
                lzTableRef.current.scrollTo(0, 0);
                getRolesApi({
                    config,
                    view,
                    groupBy,
                    containInherited,
                    filter,
                    pagination: { start: 0 },
                })
                    .then((res) => {
                        if (res.total > 0) {
                            setTotal(res.total);
                            setRoles(preprocessData(res.data, groupBy, containInherited));
                            const newPagination = {
                                start: PAGE_SIZE,
                            };
                            setPagination(newPagination);
                            setActionResultData(data);
                            resetDestination();

                            setSelected({});
                            setOpenDeleteDialog(false);
                            setOpenDeleteResult(true);
                            setDestinationFilled(false);
                        }
                    })
                    .catch((error) => console.log(error))
                    .finally(() => setHandlingAction(false));
            })
            .catch((error) => {
                console.log(error);
                setHandlingAction(false);
                addErrorMessage('Something went wrong');
                handleSubmitError();
            });
    };

    const getViewOptions = async (config) => {
        const options = await getViewOptionsApi({ config });
        setViewOptions(options.map((o) => o.value));
        setView(options.map((o) => o.value)[0]);
        if (options.length === 0) {
            setFirstLoadingTable(false);
            addErrorMessage('No view found');
        }
    };

    const getSelectOptions = () => {
        setFirstLoadingTable(true);
        getConfigurationsApi()
            .then((data) => {
                if (data.length > 0) {
                    setConfigOptions(data.map((config) => config.name));
                    setConfig(data[0].name);
                    getViewOptions(data[0].name);
                }
            })
            .catch((error) => {
                setFirstLoadingTable(false);
                addErrorMessage('Failed to load Configurations');
            });
    };

    const getRoles = () => {
        setFirstLoadingTable(true);

        getRolesApi({ config, view, groupBy, containInherited, filter, pagination: { start: 0 } })
            .then((res) => {
                if (res.total > 0) {
                    setTotal(res.total);
                    setRoles(preprocessData(res.data, groupBy, containInherited));

                    const newPagination = {
                        start: PAGE_SIZE,
                    };
                    setPagination(newPagination);
                }
            })
            .catch((error) => console.log(error))
            .finally(() => setFirstLoadingTable(false));
    };

    const getDeploymentOptions = () => {
        if (!deploymentOptionSelected?.deploymentOptionParam) return;
        setDeploymentOptionData(null);
        getDeploymentOptionApi(deploymentOptionSelected?.deploymentOptionParam)
            .then((res) => {
                setDeploymentOptionData(res?.data);
            })
            .catch((error) => console.log(error));
    };

    const handleGetOptionDNS = (data) => {
        setSelectedDeploymentOption(data);
    };

    const handleGetDeploymentDataFromDialog = (data) => {
        setDeploymentDataFromDialog(data);
    };

    useEffect(() => {
        if (config && view) getRoles();
    }, [config, view, groupBy, containInherited, filter]);

    useEffect(() => {
        getSelectOptions();
    }, []);

    useEffect(() => {
        getDeploymentOptions();
    }, [deploymentOptionSelected]);

    return (
        <AppContext.Provider value={{ config, view }}>
            <div className='RoleMnt'>
                <div className={`${groupObjSelected ? 'left-content' : ''}`} style={{ flex: 1 }}>
                    <div className='RoleMnt-wrapper'>
                        <div className='RoleMnt-form'>
                            <DropDownField
                                label='Configuration'
                                className='RoleMnt-form__configField'
                                options={configOptions}
                                renderOption={(value) => value}
                                value={config}
                                onChange={handleConfigChange}
                            />
                            <DropDownField
                                label='View'
                                className='RoleMnt-form__viewField'
                                value={view}
                                options={viewOptions}
                                renderOption={(value) => value}
                                onChange={handleViewChange}
                            />
                            <DropDownField
                                label='Group By'
                                className='RoleMnt-form__groupField'
                                value={groupBy}
                                options={GROUPBY_OPTIONS}
                                renderOption={(option) => option.label}
                                onChange={handleGroupChange}
                            />
                            <DropDownField
                                label='Show Inherited Roles'
                                className='RoleMnt-form__inheritField'
                                value={containInherited}
                                options={INHERIT_OPTIONS}
                                renderOption={(option) => option.label}
                                onChange={handleChangeInherited}
                            />
                        </div>

                        <Layer className='RoleMnt-tableWrapper'>
                            {/* <TableTitle title='Roles' /> */}

                            <TableToolbar className='RoleMnt-tableToolbar'>
                                <TableToolbarDefault
                                    className='RoleMnt-tableToolbar--default'
                                    hidden={false}>
                                    <IconMenu
                                        aria-label='Select an option'
                                        disabled={!hasChecked()}
                                        tooltipText={`Actions`}
                                        tooltipPlacement='top'>
                                        {(groupBy.value === 'zone'
                                            ? ZONE_ROLE_ACTIONS
                                            : ROLE_ACTIONS
                                        ).map((action) => (
                                            <IconMenuItem
                                                text={action.text}
                                                onClick={() => handleChoseAction(action)}
                                            />
                                        ))}
                                    </IconMenu>
                                    <Filter filter={filter} onChangeFilter={handleFilterChange} />
                                </TableToolbarDefault>
                            </TableToolbar>

                            <LazyLoadTable
                                ref={lzTableRef}
                                roles={roles}
                                firstLoadingTable={firstLoadingTable}
                                total={total}
                                containInherited={containInherited}
                                groupBy={groupBy}
                                filter={filter}
                                columns={columns}
                                onChangeRoles={(newData) =>
                                    setRoles(preprocessData(newData, groupBy, containInherited))
                                }
                                pageSize={PAGE_SIZE}
                                pagination={pagination}
                                onChangePagination={(newPagination) => setPagination(newPagination)}
                                handleClickDetail={handleClickDetail}
                                rowSelected={rowSelected}
                                selected={selected}
                                onChangeSelected={(newSelected) => setSelected(newSelected)}
                            />
                        </Layer>
                    </div>

                    {openDeleteDialog && !handlingValidation && (
                        <Dialog title='Confirm Delete Roles'>
                            <DeleteRoleConfirm
                                roles={roles}
                                groupBy={groupBy}
                                selected={selected}
                                selectedAction={selectedAction}
                                destination={destination}
                                validationData={validationData}
                                onChangeHandlingAction={(v) => setHandlingAction(v)}
                            />
                            <div className='ConfirmDialog__buttons'>
                                <Button
                                    text='Cancel'
                                    tabindex={-1}
                                    onClick={handleCancelDeleteConfirm}
                                />
                                <Button
                                    text='Submit'
                                    type='primary'
                                    disabled={validationData.some(
                                        (o) => o.status === 'UNAVAILABLE',
                                    )}
                                    onClick={handleConfirmAcceptDelete}
                                />
                            </div>
                        </Dialog>
                    )}

                    {actionResultData && !openDeleteDialog && (
                        <Dialog
                            className='resultDialog'
                            title={`Result ${selectedAction.text}`}
                            initialFocus={false}>
                            <div className='resultDialog__item'>
                                <ActionResultTable
                                    isDeleteResult={openDeleteResult}
                                    data={actionResultData}
                                />
                            </div>
                            <div className='resultDialog__buttons'>
                                <Button
                                    text='Close'
                                    onClick={() => {
                                        setActionResultData(null);
                                        setOpenDeleteResult(false);
                                        setSelectedAction(null);
                                    }}
                                />
                            </div>
                        </Dialog>
                    )}

                    {showModal && (
                        <Dialog
                            className={`Dialog${showConfirm ? '--confirm' : ''}`}
                            title={
                                showConfirm ? `Confirm ${selectedAction.text}` : selectedAction.text
                            }
                            initialFocus={false}>
                            <div>
                                <div className={`Dialog__item${showConfirm ? '--confirm' : ''}`}>
                                    {showConfirm && (
                                        <Confirm
                                            selectedAction={selectedAction}
                                            selected={selected}
                                            destination={destination}
                                            validationData={validationData}
                                            roles={roles}
                                            groupBy={groupBy}
                                            view={view}
                                            onChangeHandlingAction={(v) => setHandlingAction(v)}
                                            handleGetDeploymentDataFromDialog={
                                                handleGetDeploymentDataFromDialog
                                            }
                                            handleGetOptionDNS={handleGetOptionDNS}
                                        />
                                    )}
                                    {showDestination && (
                                        <DestinationForm
                                            selectedActionName={selectedAction.name}
                                            destination={destination}
                                            onChange={(fieldName, updated) => {
                                                setDestination({
                                                    ...destination,
                                                    [fieldName]: updated,
                                                });
                                            }}
                                            onChangeMultiple={(newValues) =>
                                                setDestination({ ...destination, ...newValues })
                                            }
                                        />
                                    )}
                                </div>
                            </div>
                            <div className='ConfirmDialog__buttons'>
                                <Button text='Cancel' tabindex={-1} onClick={handleCancel} />
                                {!showConfirm ? (
                                    <Button
                                        text={selectedAction.actionText}
                                        type='primary'
                                        onClick={() => handleSubmitForm()}
                                        disabled={
                                            !checkDestinationFill({
                                                destination,
                                                selectedAction,
                                            })
                                        }
                                    />
                                ) : (
                                    <Button
                                        text='Submit'
                                        type='primary'
                                        disabled={validationData.some(
                                            (x) =>
                                                x.status !== 'AVAILABLE' &&
                                                x.status !== 'WARNING' &&
                                                x.status !== 'INFO',
                                        )}
                                        onClick={handleConfirmAccept}
                                    />
                                )}
                            </div>
                        </Dialog>
                    )}

                    {actionResultData && !openDeleteDialog && !openDeleteResult && (
                        <Dialog
                            className='resultDialog'
                            title={`Result ${selectedAction.text}`}
                            initialFocus={false}>
                            <div className='resultDialog__item'>
                                <ActionResultTable data={actionResultData} />
                            </div>
                            <div className='resultDialog__buttons'>
                                <Button
                                    text='Close'
                                    onClick={() => {
                                        setActionResultData(null);
                                        setSelectedAction(null);
                                    }}
                                />
                            </div>
                        </Dialog>
                    )}
                </div>
                {detailGroupPanel}
            </div>
            {((firstLoadingTable && total === 0) || handlingAction || handlingValidation) && (
                <ModalSpinner />
            )}
        </AppContext.Provider>
    );
}

export default App;
