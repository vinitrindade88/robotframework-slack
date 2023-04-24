import slack
from const_messages import principal_block, start_suite_message, tread_error_message


class RobotframeworkSlackNotification:

    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.2.0'

    def __init__(self,
                 slack_token: str,
                 channel_id: str,
                 application: str,
                 environment: str,
                 branch: str,
                 cicd_url: str,
                 cicd_id: str,
                 devicefarm_url: str):

        self.slack_token = slack_token
        self.channel_id = channel_id
        self.application = application
        self.environment = environment
        self.branch = branch
        self.cicd_url = cicd_url
        self.cicd_id = cicd_id
        self.devicefarm_url = devicefarm_url
        self.client = slack.WebClient(token=slack_token)
        self.message_timestamp = []

    def start_suite(self, data, result):
        message = self._build_principal_message(result, self.application, self.environment, 0, 0, 0, 0)
        ts = self._post_principal_message(result, message)
        self.message_timestamp.append(ts)

    def end_suite(self, data, result):
        statistics = self._robot_statistic(result.statistics)

        count_pass = statistics.passed
        count_failed = statistics.failed
        count_skipped = statistics.skipped
        count_total = statistics.total

        message = self._build_principal_message(result, self.application, self.environment, count_total, count_pass, count_failed,
                                                count_skipped)
        self._update_principal_message(result, self.message_timestamp[0], message)

    def end_test(self, data, result):
        attachment_color = self._attachment_color(result)
        message = self._build_thread_message(result, attachment_color)
        self._post_thread_message(result, message, self.message_timestamp[0])

    def _robot_statistic(self, statistics):
        try:
            if statistics.total:
                return statistics  # robotframework < 4.0.0
        except:
            return statistics.all  # robotframework > 4.0.0

    def _post_principal_message(self, result, message):
        if not result.parent:
            response = self.client.chat_postMessage(channel=self.channel_id, blocks=message)
            return response['ts']

    def _post_thread_message(self, result, message, message_ts):
        if result.failed or result.skipped:
            self.client.chat_postMessage(channel=self.channel_id, attachments=message, thread_ts=message_ts)

    def _update_principal_message(self, result, message_timestamp, message):
        if not result.parent:
            self.client.chat_update(channel=self.channel_id, blocks=message, ts=message_timestamp)

    def _build_principal_message(self, result, application, environment, executions, success_executions, failed_executions, skipped_executions):
        '''
        Builds the main message block
        '''

        if result.passed == False and result.failed == False:
            start_suite_message[7]['text']['text'] = f'*CICD*: *<{self.cicd_url}|{self.cicd_id}>* || *BrowserStack*: *<{self.devicefarm_url}|{cicd_id}>*'

            return start_suite_message
        else:
            result_status = result.status

            if result.passed:
                result_icon = ":large_green_circle:"
            elif result.failed:
                result_icon = ":red_circle:"
            else:
                result_icon = ":white_circle:"

            principal_block[0]['text']['text'] = f'Aplicación en prueba:  {application}'
            principal_block[1]['text']['text'] = f'*Branch*: {self.branch} || *Enterno*: {environment}'
            principal_block[4]['text']['text'] = f'{result_icon} *{result_status}*'

            principal_block[7]['fields'][0]['text'] = f'*Pruebas Ejecutadas:*\n{executions}'
            principal_block[7]['fields'][1]['text'] = f'*Probado con éxito:*\n{success_executions}'

            principal_block[8]['fields'][0]['text'] = f'*Probado con error:*\n{failed_executions}'
            principal_block[8]['fields'][1]['text'] = f'*Pruebas salteadas:*\n{skipped_executions}'

            principal_block[11]['text']['text'] = f'*CICD*: *<{self.cicd_url}|{self.cicd_id}>* || *BrowserStack*: *<{self.devicefarm_url}|{self.cicd_id}>*'

            return principal_block

    def _build_thread_message(self, result, attachment_color):
        tread_error_message[0]['color'] = f'{attachment_color}'
        tread_error_message[0]['blocks'][0]['text']['text'] = f'{result.name}'
        tread_error_message[0]['blocks'][3]['text']['text'] = f'{result.name}'

        return tread_error_message

    def _attachment_color(self, result):
        color = None

        if result.passed:
            color = "1abf00"
        elif result.failed:
            color = "ff4646"
        elif result.skipped:
            color = "eddd00"

        return color
