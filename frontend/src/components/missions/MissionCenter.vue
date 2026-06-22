<template>
  <section class="missionCenter" :class="{ hasDailyMomentumBar: showDailyMomentumBar }">
    <RingoRewardSequence :steps="rewardSequenceSteps" :sprite="rewardSequenceSprite"
      @action="handleRewardSequenceAction" @finish="finishRewardSequence" />

    <BaseCard v-if="restModeActive" class="restModeCard">
      <div class="restModeSprite" aria-hidden="true">
        <img v-if="restModeSprite.src" :src="restModeSprite.src" :alt="restModeSprite.key" />
      </div>

      <div class="restModeCopy">
        <p class="eyebrow compact">{{ t("missions.restMode.eyebrow") }}</p>
        <h2>{{ t("missions.restMode.title") }}</h2>
        <p>{{ t("missions.restMode.body") }}</p>
        <p v-if="nearestFutureReminderLabel" class="restModeReminder">
          {{ t("missions.restMode.nextReminder", { time: nearestFutureReminderLabel }) }}
        </p>
      </div>

      <div class="restModeActions">
        <!-- <BaseButton variant="primary" @click="restForNow">
          {{ t("missions.restMode.restCta") }}
        </BaseButton> -->
        <BaseButton variant="secondary" @click="showDashboardFromRest">
          {{ t("missions.restMode.dashboardCta") }}
        </BaseButton>
      </div>
    </BaseCard>

    <BaseCard v-else-if="coachActionPanel" class="coachActionPanel"
      :class="{ complete: !!todaySavedLabel, firstRunRevealPanel: props.firstRunFocus }">
      <RingoCoach v-if="showCoach" embedded :message="coachMessage" :sprite="coachSprite"
        :primary-action="coachPrimaryAction" :secondary-action="coachSecondaryAction"
        :class="{ firstRunRevealStep: props.firstRunFocus, firstRunRevealCoach: props.firstRunFocus }"
        @action="handleCoachAction" />

      <div v-if="showFirstRunMissionIntro" class="firstRunMissionIntro firstRunRevealStep firstRunRevealIntro">
        <p class="eyebrow compact">{{ t("missions.firstRunFocus.eyebrow") }}</p>
        <h3>{{ t("missions.firstRunFocus.title") }}</h3>
        <p>{{ t("missions.firstRunFocus.text") }}</p>
      </div>

      <DailyMomentumBar v-if="showDailyMomentumBar" :today-safe="dailyMomentumTodaySafe"
        :streak-count="dailyMomentumStreakCount" :path-groups="dailyMomentumPathGroups" :actions="dailyMomentumActions"
        :show-explore-paths="showDailyMomentumExplorePaths" @select-path="selectDailyMomentumPath"
        @action="handleDailyMomentumAction" @explore-paths="exploreDailyMomentumPaths"
        @explain-strike="explainDailyMomentumStrike" />

      <ExplorePathsPanel :open="explorePathsPanelOpen" :paths="dailyMomentumExplorePathItems"
        @close="closeExplorePathsPanel" @open-paths="openPathsFromExplorePanel" />

      <div v-if="showFocusMissionCard" :id="`mission-${focusMission.mission_id}`" class="focusMission coachFocusMission"
        :class="{ firstRunRevealStep: props.firstRunFocus, firstRunRevealMission: props.firstRunFocus }">
        <MissionContextPanel :mission="focusMission" :heading="t('missions.ringoSuggestedMission')"
          :intensity-meta="focusMissionIntensity" :parent-title="parentMissionFor(focusMission)?.title || ''"
          :reminder-label="missionReminderContextLabel(focusMission)" :status-copy="missionStatusCopy(focusMission)"
          :reminder-delivery-meta="reminderDeliveryMeta(focusMission)" />
        <div v-if="showFocusMissionActions" class="missionActions primaryMissionActions">
          <BaseButton variant="primary" :loading="busyId === focusMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(focusMission, 'done')" @click="markDone(focusMission)">
            <img v-if="missionActionIcon('done')" :src="missionActionIcon('done')" alt="" class="missionActionIcon"
              aria-hidden="true" />
            {{ missionHasStatus(focusMission, "remind_later") ? t("missions.doItNow") : t("missions.doneCta") }}
          </BaseButton>

          <BaseButton variant="secondary" :loading="busyId === focusMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(focusMission, 'done')" @click="remindLater(focusMission)">
            <img v-if="missionActionIcon('remindLater')" :src="missionActionIcon('remindLater')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ missionHasStatus(focusMission, "remind_later") ? t("missions.editReminder") : t("missions.remindLater")
            }}
          </BaseButton>

          <BaseButton v-if="shouldShowFocusSupportAction('make_smaller', focusMission)" variant="secondary"
            @click="handleFocusSupportAction('make_smaller', focusMission)">
            <img v-if="missionActionIcon('makeSmaller')" :src="missionActionIcon('makeSmaller')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.make_smaller") }}
          </BaseButton>

          <BaseButton v-if="shouldShowFocusSupportAction('too_tired', focusMission)" variant="secondary"
            @click="handleFocusSupportAction('too_tired', focusMission)">
            <img v-if="missionActionIcon('tooTired')" :src="missionActionIcon('tooTired')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.too_tired") }}
          </BaseButton>

          <BaseButton v-if="shouldShowFullVersionAction(focusMission)" variant="secondary"
            @click="focusMainMissionVariant(focusMission)">
            <img v-if="missionActionIcon('makeBigger')" :src="missionActionIcon('makeBigger')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.useFullVersion") }}
          </BaseButton>

          <BaseButton variant="secondary" :loading="busyId === focusMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(focusMission, 'done', 'skipped')" @click="skipMission(focusMission)">
            <img v-if="missionActionIcon('skip')" :src="missionActionIcon('skip')" alt="" class="missionActionIcon"
              aria-hidden="true" />
            {{ missionHasStatus(focusMission, "skipped") ? t("missions.skipped") : t("missions.skip") }}
          </BaseButton>
        </div>

        <div v-if="showFirstRunActionEducation"
          class="missionActionEducation firstRunRevealStep firstRunRevealEducation"
          :aria-label="t('missions.firstRunEducation.label')">
          <div class="educationItem">
            <strong>{{ t("missions.firstRunEducation.done.title") }}</strong>
            <span>{{ t("missions.firstRunEducation.done.text") }}</span>
          </div>

          <div class="educationItem">
            <strong>{{ t("missions.firstRunEducation.smaller.title") }}</strong>
            <span>{{ t("missions.firstRunEducation.smaller.text") }}</span>
          </div>

          <div class="educationItem">
            <strong>{{ t("missions.firstRunEducation.remind.title") }}</strong>
            <span>{{ t("missions.firstRunEducation.remind.text") }}</span>
          </div>

          <div class="educationItem">
            <strong>{{ t("missions.firstRunEducation.skip.title") }}</strong>
            <span>{{ t("missions.firstRunEducation.skip.text") }}</span>
          </div>
        </div>

        <div v-if="isReminderPanelOpen(focusMission)" class="remindOptionsPanel">
          <p>{{ t("missions.remindOptions.prompt") }}</p>
          <div class="remindOptions">
            <BaseButton v-for="option in reminderOptions" :key="option.key" variant="secondary"
              :loading="isReminderOptionLoading(focusMission, option.key)"
              :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
              @click="selectReminderOption(focusMission, option)">
              {{ option.label }}
            </BaseButton>
            <BaseButton variant="secondary" :loading="isReminderOptionLoading(focusMission, 'ringo')"
              :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
              @click="planMissionReminder(focusMission)">
              {{ t("missions.remindOptions.ringoPick") }}
            </BaseButton>
            <BaseButton variant="secondary" :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
              @click="openCustomReminderTime(focusMission)">
              {{ t("missions.remindOptions.customTime") }}
            </BaseButton>
            <BaseButton variant="secondary" @click="closeReminderPanel">
              {{ t("missions.backToMissionActions") }}
            </BaseButton>
          </div>
          <div v-if="isCustomReminderPanelOpen(focusMission)" class="customReminderPanel">
            <label :for="`custom-reminder-${focusMission.mission_id}`">
              {{ t("missions.remindOptions.customPrompt") }}
            </label>
            <div class="customReminderControls">
              <input :id="`custom-reminder-${focusMission.mission_id}`" v-model="customReminderTime" type="time" />
              <BaseButton variant="primary" :loading="isReminderOptionLoading(focusMission, 'custom')"
                :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
                @click="selectCustomReminderTime(focusMission)">
                {{ t("missions.remindOptions.setCustom") }}
              </BaseButton>
            </div>
            <small>{{ t("missions.remindOptions.customHelp") }}</small>
          </div>
        </div>

        <div v-if="isSkipReasonPanelOpen(focusMission)" class="skipReasonPanel">
          <p>{{ t("missions.skipReasons.prompt") }}</p>
          <div class="skipReasons">
            <BaseButton v-for="reason in skipReasonOptions" :key="reason.key" variant="secondary"
              :loading="isSkipReasonLoading(focusMission, reason.key)"
              :disabled="busyAction === 'skip' && busyId === focusMission.mission_id"
              @click="selectSkipReason(focusMission, reason)">
              {{ reason.label }}
            </BaseButton>
            <BaseButton variant="secondary" @click="closeSkipReasonPanel">
              {{ t("missions.backToMissionActions") }}
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- <p v-if="todaySavedLabel" class="todaySaved">
        <strong>{{ todaySavedLabel }}</strong>
        <span v-if="showTodaySavedBody">{{ t("missions.todaySavedBody") }}</span>
      </p> -->

      <section v-if="selectedOptionalExplorerMission && !dueReminderFocusActive" id="optional-explorer-selected"
        class="optionalNextStep optionalExplorerSelected">
        <div class="optionalNextCopy">
          <p class="eyebrow compact">{{ t("missions.optionalExplorerList.eyebrow") }}</p>
          <h3>{{ t("missions.optionalExplorerSelectedTitle") }}</h3>
          <p>{{ selectedOptionalExplorerBody }}</p>
        </div>

        <div class="optionalNextMission">
          <MissionContextPanel :mission="selectedOptionalExplorerMission"
            :heading="t('missions.optionalExplorerSelectedTitle')"
            :intensity-meta="buildMissionIntensityMeta(selectedOptionalExplorerMission, { optionalContext: true })"
            :parent-title="parentMissionFor(selectedOptionalExplorerMission)?.title || ''"
            :reminder-label="missionReminderContextLabel(selectedOptionalExplorerMission)"
            :status-copy="missionStatusCopy(selectedOptionalExplorerMission)"
            :reminder-delivery-meta="reminderDeliveryMeta(selectedOptionalExplorerMission)" />
        </div>

        <div v-if="showMissionItemActions(selectedOptionalExplorerMission)"
          class="missionActions optionalExplorerSelectedActions">
          <BaseButton variant="primary"
            :loading="busyId === selectedOptionalExplorerMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(selectedOptionalExplorerMission, 'done')"
            @click="markDone(selectedOptionalExplorerMission)">
            <img v-if="missionActionIcon('done')" :src="missionActionIcon('done')" alt="" class="missionActionIcon"
              aria-hidden="true" />
            {{ missionHasStatus(selectedOptionalExplorerMission, "remind_later") ? t("missions.doItNow") :
              t("missions.doneCta") }}
          </BaseButton>

          <BaseButton variant="secondary"
            :loading="busyId === selectedOptionalExplorerMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(selectedOptionalExplorerMission, 'done')"
            @click="remindLater(selectedOptionalExplorerMission)">
            <img v-if="missionActionIcon('remindLater')" :src="missionActionIcon('remindLater')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ missionHasStatus(selectedOptionalExplorerMission, "remind_later") ? t("missions.editReminder") :
              t("missions.remindLater") }}
          </BaseButton>

          <BaseButton v-if="shouldShowMissionItemTinyAction(selectedOptionalExplorerMission)" variant="secondary"
            @click="focusTinyMissionVariant(selectedOptionalExplorerMission)">
            <img v-if="missionActionIcon('makeSmaller')" :src="missionActionIcon('makeSmaller')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.tryTinyVersion") }}
          </BaseButton>

          <BaseButton v-if="shouldShowFullVersionAction(selectedOptionalExplorerMission)" variant="secondary"
            @click="focusMainMissionVariant(selectedOptionalExplorerMission)">
            <img v-if="missionActionIcon('makeBigger')" :src="missionActionIcon('makeBigger')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.useFullVersion") }}
          </BaseButton>

          <BaseButton variant="secondary"
            :loading="busyId === selectedOptionalExplorerMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(selectedOptionalExplorerMission, 'done', 'skipped')"
            @click="skipMission(selectedOptionalExplorerMission)">
            <img v-if="missionActionIcon('skip')" :src="missionActionIcon('skip')" alt="" class="missionActionIcon"
              aria-hidden="true" />
            {{ missionHasStatus(selectedOptionalExplorerMission, "skipped") ? t("missions.skipped") :
              t("missions.skip") }}
          </BaseButton>
        </div>

        <div v-if="isReminderPanelOpen(selectedOptionalExplorerMission)" class="remindOptionsPanel">
          <p>{{ t("missions.remindOptions.prompt") }}</p>
          <div class="remindOptions">
            <BaseButton v-for="option in reminderOptions" :key="option.key" variant="secondary"
              :loading="isReminderOptionLoading(selectedOptionalExplorerMission, option.key)"
              :disabled="busyAction === 'remind' && busyId === selectedOptionalExplorerMission.mission_id"
              @click="selectReminderOption(selectedOptionalExplorerMission, option)">
              {{ option.label }}
            </BaseButton>
            <BaseButton variant="secondary" :loading="isReminderOptionLoading(selectedOptionalExplorerMission, 'ringo')"
              :disabled="busyAction === 'remind' && busyId === selectedOptionalExplorerMission.mission_id"
              @click="planMissionReminder(selectedOptionalExplorerMission)">
              {{ t("missions.remindOptions.ringoPick") }}
            </BaseButton>
            <BaseButton variant="secondary"
              :disabled="busyAction === 'remind' && busyId === selectedOptionalExplorerMission.mission_id"
              @click="openCustomReminderTime(selectedOptionalExplorerMission)">
              {{ t("missions.remindOptions.customTime") }}
            </BaseButton>
            <BaseButton variant="secondary" @click="closeReminderPanel">
              {{ t("missions.backToMissionActions") }}
            </BaseButton>
          </div>
          <div v-if="isCustomReminderPanelOpen(selectedOptionalExplorerMission)" class="customReminderPanel">
            <label :for="`optional-custom-reminder-${selectedOptionalExplorerMission.mission_id}`">
              {{ t("missions.remindOptions.customPrompt") }}
            </label>
            <div class="customReminderControls">
              <input :id="`optional-custom-reminder-${selectedOptionalExplorerMission.mission_id}`"
                v-model="customReminderTime" type="time" />
              <BaseButton variant="primary"
                :loading="isReminderOptionLoading(selectedOptionalExplorerMission, 'custom')"
                :disabled="busyAction === 'remind' && busyId === selectedOptionalExplorerMission.mission_id"
                @click="selectCustomReminderTime(selectedOptionalExplorerMission)">
                {{ t("missions.remindOptions.setCustom") }}
              </BaseButton>
            </div>
            <small>{{ t("missions.remindOptions.customHelp") }}</small>
          </div>
        </div>

        <div v-if="isSkipReasonPanelOpen(selectedOptionalExplorerMission)" class="skipReasonPanel">
          <p>{{ t("missions.skipReasons.prompt") }}</p>
          <div class="skipReasons">
            <BaseButton v-for="reason in skipReasonOptions" :key="reason.key" variant="secondary"
              :loading="isSkipReasonLoading(selectedOptionalExplorerMission, reason.key)"
              :disabled="busyAction === 'skip' && busyId === selectedOptionalExplorerMission.mission_id"
              @click="selectSkipReason(selectedOptionalExplorerMission, reason)">
              {{ reason.label }}
            </BaseButton>
            <BaseButton variant="secondary" @click="closeSkipReasonPanel">
              {{ t("missions.backToMissionActions") }}
            </BaseButton>
          </div>
        </div>

        <div v-if="!showDailyMomentumBar" class="optionalNextActions">
          <BaseButton variant="primary" @click="finishForToday">
            <img v-if="missionActionIcon('finishToday')" :src="missionActionIcon('finishToday')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.finishForToday") }}
          </BaseButton>
          <BaseButton variant="secondary" @click="backToOptionalChoices">
            {{ t("missions.backToOptionalChoices") }}
          </BaseButton>
        </div>
      </section>

      <section v-else-if="isTodaySaved && optionalNextMission" class="optionalNextStep">
        <div class="optionalNextCopy">
          <p class="eyebrow compact">{{ t("missions.optionalNextEyebrow") }}</p>
          <h3>{{ t("missions.optionalNextTitle") }}</h3>
          <p>{{ t("missions.optionalNextBody") }}</p>
        </div>

        <div class="optionalNextMission">
          <MissionContextPanel :mission="optionalNextMission" :heading="t('missions.optionalNextTitle')"
            :intensity-meta="optionalNextMissionIntensity"
            :parent-title="parentMissionFor(optionalNextMission)?.title || ''"
            :reminder-label="missionReminderContextLabel(optionalNextMission)"
            :status-copy="missionStatusCopy(optionalNextMission)"
            :reminder-delivery-meta="reminderDeliveryMeta(optionalNextMission)" />
        </div>

        <div class="optionalNextActions">
          <BaseButton v-if="!showDailyMomentumBar" variant="primary" @click="finishForToday">
            <img v-if="missionActionIcon('finishToday')" :src="missionActionIcon('finishToday')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.finishForToday") }}
          </BaseButton>
          <BaseButton variant="secondary" :loading="busyId === optionalNextMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(optionalNextMission, 'done')" @click="markDone(optionalNextMission)">
            <img v-if="missionActionIcon('done')" :src="missionActionIcon('done')" alt="" class="missionActionIcon"
              aria-hidden="true" />
            {{
              normalizedMissionIntensity(optionalNextMission) === "bonus"
                ? t("missions.bonusDoneCta")
                : t("missions.doneCta")
            }}
          </BaseButton>
          <BaseButton variant="secondary"
            :loading="busyId === optionalNextMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(optionalNextMission, 'done')"
            @click="remindOptionalNextMission(optionalNextMission)">
            <img v-if="missionActionIcon('remindLater')" :src="missionActionIcon('remindLater')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ missionHasStatus(optionalNextMission, "remind_later") ? t("missions.editReminder") :
              t("missions.remindLater") }}
          </BaseButton>
          <BaseButton v-if="shouldShowOptionalNextSupportAction('make_smaller', optionalNextMission)"
            variant="secondary" @click="handleOptionalNextSupportAction('make_smaller', optionalNextMission)">
            <img v-if="missionActionIcon('makeSmaller')" :src="missionActionIcon('makeSmaller')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.make_smaller") }}
          </BaseButton>
          <BaseButton v-if="shouldShowOptionalNextSupportAction('too_tired', optionalNextMission)" variant="secondary"
            @click="handleOptionalNextSupportAction('too_tired', optionalNextMission)">
            <img v-if="missionActionIcon('tooTired')" :src="missionActionIcon('tooTired')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.too_tired") }}
          </BaseButton>
          <BaseButton variant="secondary" :loading="busyId === optionalNextMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(optionalNextMission, 'skipped')"
            @click="skipOptionalNextMission(optionalNextMission)">
            <img v-if="missionActionIcon('skip')" :src="missionActionIcon('skip')" alt="" class="missionActionIcon"
              aria-hidden="true" />
            {{ t("missions.skip") }}
          </BaseButton>
        </div>
      </section>

      <RemainingMissionExplorer v-if="showOptionalMissionExplorer" :missions="optionalExplorerMissions"
        :selected-mission-id="selectedOptionalExplorerMissionId" :selected-path-id="selectedMomentumPathId"
        :hide-actions="showDailyMomentumBar" @select="selectOptionalExplorerMission"
        @select-path="selectOptionalExplorerPath" @select-challenge="selectOptionalExplorerChallenge"
        @back="showOptionalExplorerRoot" @close="hideOptionalMissionExplorer" @finish="finishForToday" />

      <section v-if="showOptionalExplorerPrompt" class="optionalExplorerPrompt">
        <div class="optionalNextCopy">
          <p class="eyebrow compact">{{ t("missions.optionalExplorerEyebrow") }}</p>
          <h3>{{ t("missions.optionalExplorerTitle") }}</h3>
          <p>{{ t("missions.optionalExplorerBody") }}</p>
        </div>

        <div class="optionalExplorerActions">
          <BaseButton variant="primary" @click="finishForToday">
            <img v-if="missionActionIcon('finishToday')" :src="missionActionIcon('finishToday')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.finishForToday") }}
          </BaseButton>
          <span v-if="futureReminderCount" class="optionalReminderQueue">
            {{ t("missions.futureReminderQueue", { count: futureReminderCount }) }}
          </span>
          <BaseButton v-if="optionalSuggestionAvailable" variant="secondary" @click="suggestOptionalStep">
            <img v-if="missionActionIcon('optionalStep')" :src="missionActionIcon('optionalStep')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.suggestOptionalStep") }}
          </BaseButton>
          <BaseButton v-if="optionalExplorerMissions.length" variant="secondary" @click="viewRemainingMissions">
            <img v-if="missionActionIcon('viewChoices')" :src="missionActionIcon('viewChoices')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.viewOptionalMissions") }}
          </BaseButton>
        </div>
      </section>

      <div v-if="showCompletedChoices" class="completedChoices">
        <BaseButton v-if="!optionalNextMission" variant="primary" @click="finishForToday">
          <img v-if="missionActionIcon('finishToday')" :src="missionActionIcon('finishToday')" alt=""
            class="missionActionIcon" aria-hidden="true" />
          {{ t("missions.finishForToday") }}
        </BaseButton>

        <!-- <RouterLink v-if="detailsMission?.enrollment_id" class="missionGuideLink"
          :to="`/enrollment/${detailsMission.enrollment_id}`">
          {{ t("missions.detailsCta") }}
        </RouterLink> -->

      </div>

    </BaseCard>

    <UiState :loading="loading" :error="!!error" :empty="false" :loading-title="t('missions.loadingTitle')"
      :loading-text="t('missions.loadingText')" :error-title="t('missions.errorTitle')"
      :error-text="error || t('common.pleaseTryAgain')" @retry="loadMissions" />

    <!-- <p v-if="showMissionNotice" class="missionNotice" :class="noticeType">
      {{ notice }}
    </p> -->

    <BaseCard v-if="telegramReminderPrompt" ref="telegramPromptRef" class="telegramReminderPrompt"
      :class="telegramReminderPrompt.mode">
      <div>
        <p class="eyebrow compact">{{ t("missions.telegramPrompt.eyebrow") }}</p>
        <h3>{{ t(`missions.telegramPrompt.${telegramReminderPrompt.mode}Title`) }}</h3>
        <p>{{ t(`missions.telegramPrompt.${telegramReminderPrompt.mode}Body`) }}</p>
      </div>

      <div v-if="telegramConnectCode" class="telegramConnectCode">
        <span>{{ t("missions.telegramPrompt.connectCode") }}</span>
        <strong>{{ telegramConnectCode.code }}</strong>
        <small>{{ t("missions.telegramPrompt.manualFallback") }}</small>
      </div>

      <p v-if="telegramPromptError" class="telegramPromptError">
        {{ telegramPromptError }}
      </p>

      <div class="telegramPromptActions">
        <BaseButton v-if="telegramReminderPrompt.mode === 'connect'" variant="primary" :loading="telegramPromptBusy"
          @click="connectTelegramFromReminder">
          {{ t("missions.telegramPrompt.connectCta") }}
        </BaseButton>
        <BaseButton v-if="telegramReminderPrompt.mode === 'disabled'" variant="primary" :loading="telegramPromptBusy"
          @click="enableTelegramRemindersFromPrompt">
          {{ t("missions.telegramPrompt.enableCta") }}
        </BaseButton>
        <a v-if="telegramConnectLink" class="telegramBotLink" :href="telegramConnectLink" target="_blank"
          rel="noreferrer">
          {{ t("missions.telegramPrompt.openBot") }}
        </a>
        <!-- <RouterLink class="telegramBotLink" to="/profile">
          {{ t("missions.telegramPrompt.settingsCta") }}
        </RouterLink> -->
        <BaseButton variant="secondary" @click="dismissTelegramReminderPrompt">
          {{ t("missions.telegramPrompt.laterCta") }}
        </BaseButton>
      </div>
    </BaseCard>

    <PathSelection v-if="!loading && !error && showPathSelection"
      :allow-active-start="ringo?.state === 'path_selected_no_challenge'" @started="loadMissions" />

    <BaseCard v-if="missionGuide && !coachActionPanel" class="missionGuide"
      :class="[missionGuide.state, { complete: missionGuide.complete }]">
      <div class="missionGuideCopy">
        <p class="eyebrow compact">{{ t("missions.guideEyebrow") }}</p>
        <h2>{{ missionGuide.title }}</h2>
        <p>{{ missionGuide.body }}</p>
      </div>

      <div class="missionStepper" :aria-label="t('missions.stepperLabel')">
        <span class="step complete">{{ t("missions.steps.path") }}</span>
        <span class="step" :class="{ complete: missionGuide.complete, active: !missionGuide.complete }">
          {{ t("missions.steps.mission") }}
        </span>
        <span class="step" :class="{ complete: missionGuide.complete }">
          {{ t("missions.steps.reward") }}
        </span>
      </div>

      <div v-if="focusMission && !coachActionPanel" :id="`mission-${focusMission.mission_id}`" class="focusMission">
        <MissionContextPanel :mission="focusMission"
          :heading="guidanceMission ? t('missions.ringoSuggestedMission') : t('missions.nextMission')"
          :intensity-meta="focusMissionIntensity" :parent-title="parentMissionFor(focusMission)?.title || ''"
          :reminder-label="missionReminderContextLabel(focusMission)" :status-copy="missionStatusCopy(focusMission)"
          :reminder-delivery-meta="reminderDeliveryMeta(focusMission)" />
        <div v-if="showFocusMissionActions" class="missionActions primaryMissionActions">
          <BaseButton variant="primary" :loading="busyId === focusMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(focusMission, 'done')" @click="markDone(focusMission)">
            <img v-if="missionActionIcon('done')" :src="missionActionIcon('done')" alt="" class="missionActionIcon"
              aria-hidden="true" />
            {{ missionHasStatus(focusMission, "remind_later") ? t("missions.doItNow") : t("missions.doneCta") }}
          </BaseButton>

          <BaseButton variant="secondary" :loading="busyId === focusMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(focusMission, 'done')" @click="remindLater(focusMission)">
            <img v-if="missionActionIcon('remindLater')" :src="missionActionIcon('remindLater')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ missionHasStatus(focusMission, "remind_later") ? t("missions.editReminder") : t("missions.remindLater")
            }}
          </BaseButton>

          <BaseButton v-if="shouldShowFocusSupportAction('make_smaller', focusMission)" variant="secondary"
            @click="handleFocusSupportAction('make_smaller', focusMission)">
            <img v-if="missionActionIcon('makeSmaller')" :src="missionActionIcon('makeSmaller')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.make_smaller") }}
          </BaseButton>

          <BaseButton v-if="shouldShowFocusSupportAction('too_tired', focusMission)" variant="secondary"
            @click="handleFocusSupportAction('too_tired', focusMission)">
            <img v-if="missionActionIcon('tooTired')" :src="missionActionIcon('tooTired')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.too_tired") }}
          </BaseButton>

          <BaseButton v-if="shouldShowFullVersionAction(focusMission)" variant="secondary"
            @click="focusMainMissionVariant(focusMission)">
            <img v-if="missionActionIcon('makeBigger')" :src="missionActionIcon('makeBigger')" alt=""
              class="missionActionIcon" aria-hidden="true" />
            {{ t("missions.ringoActions.useFullVersion") }}
          </BaseButton>

          <BaseButton variant="secondary" :loading="busyId === focusMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(focusMission, 'done', 'skipped')" @click="skipMission(focusMission)">
            <img v-if="missionActionIcon('skip')" :src="missionActionIcon('skip')" alt="" class="missionActionIcon"
              aria-hidden="true" />
            {{ missionHasStatus(focusMission, "skipped") ? t("missions.skipped") : t("missions.skip") }}
          </BaseButton>
        </div>

        <div v-if="showFirstRunActionEducation" class="missionActionEducation"
          :aria-label="t('missions.firstRunEducation.label')">
          <div class="educationItem">
            <strong>{{ t("missions.firstRunEducation.done.title") }}</strong>
            <span>{{ t("missions.firstRunEducation.done.text") }}</span>
          </div>

          <div class="educationItem">
            <strong>{{ t("missions.firstRunEducation.smaller.title") }}</strong>
            <span>{{ t("missions.firstRunEducation.smaller.text") }}</span>
          </div>

          <div class="educationItem">
            <strong>{{ t("missions.firstRunEducation.remind.title") }}</strong>
            <span>{{ t("missions.firstRunEducation.remind.text") }}</span>
          </div>

          <div class="educationItem">
            <strong>{{ t("missions.firstRunEducation.skip.title") }}</strong>
            <span>{{ t("missions.firstRunEducation.skip.text") }}</span>
          </div>
        </div>

        <div v-if="isReminderPanelOpen(focusMission)" class="remindOptionsPanel">
          <p>{{ t("missions.remindOptions.prompt") }}</p>
          <div class="remindOptions">
            <BaseButton v-for="option in reminderOptions" :key="option.key" variant="secondary"
              :loading="isReminderOptionLoading(focusMission, option.key)"
              :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
              @click="selectReminderOption(focusMission, option)">
              {{ option.label }}
            </BaseButton>
            <BaseButton variant="secondary" :loading="isReminderOptionLoading(focusMission, 'ringo')"
              :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
              @click="planMissionReminder(focusMission)">
              {{ t("missions.remindOptions.ringoPick") }}
            </BaseButton>
            <BaseButton variant="secondary" :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
              @click="openCustomReminderTime(focusMission)">
              {{ t("missions.remindOptions.customTime") }}
            </BaseButton>
            <BaseButton variant="secondary" @click="closeReminderPanel">
              {{ t("missions.backToMissionActions") }}
            </BaseButton>
          </div>
          <div v-if="isCustomReminderPanelOpen(focusMission)" class="customReminderPanel">
            <label :for="`custom-reminder-${focusMission.mission_id}`">
              {{ t("missions.remindOptions.customPrompt") }}
            </label>
            <div class="customReminderControls">
              <input :id="`custom-reminder-${focusMission.mission_id}`" v-model="customReminderTime" type="time" />
              <BaseButton variant="primary" :loading="isReminderOptionLoading(focusMission, 'custom')"
                :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
                @click="selectCustomReminderTime(focusMission)">
                {{ t("missions.remindOptions.setCustom") }}
              </BaseButton>
            </div>
            <small>{{ t("missions.remindOptions.customHelp") }}</small>
          </div>
        </div>

        <div v-if="isSkipReasonPanelOpen(focusMission)" class="skipReasonPanel">
          <p>{{ t("missions.skipReasons.prompt") }}</p>
          <div class="skipReasons">
            <BaseButton v-for="reason in skipReasonOptions" :key="reason.key" variant="secondary"
              :loading="isSkipReasonLoading(focusMission, reason.key)"
              :disabled="busyAction === 'skip' && busyId === focusMission.mission_id"
              @click="selectSkipReason(focusMission, reason)">
              {{ reason.label }}
            </BaseButton>
            <BaseButton variant="secondary" @click="closeSkipReasonPanel">
              {{ t("missions.backToMissionActions") }}
            </BaseButton>
          </div>
        </div>
      </div>

      <div class="missionGuideActions">
        <BaseButton v-if="!missionGuide.complete && !isTodaySaved && focusMission && !guidanceActions.length"
          variant="primary" @click="focusMissionCard(focusMission)">
          {{ t("missions.focusCta") }}
        </BaseButton>

        <RouterLink v-if="focusMission?.enrollment_id" class="missionGuideLink"
          :to="`/enrollment/${focusMission.enrollment_id}`">
          {{ t("missions.detailsCta") }}
        </RouterLink>

        <RouterLink v-if="missionGuide.complete" class="missionGuideLink" to="/paths">
          {{ t("missions.nextPathCta") }}
        </RouterLink>
      </div>
    </BaseCard>

    <BaseCard v-if="showSecondaryMissionStatus" class="missionList secondaryMissionList">
      <div v-if="showOtherMissions" class="missionItems">
        <div class="missionTimeline">
          <div v-if="plannableReminderCount" class="plannerCallout">
            <p>{{ t("missions.planRemindersHelp", { count: plannableReminderCount }) }}</p>
            <BaseButton variant="primary" :loading="planningReminders" :disabled="planningReminders"
              @click="planTodayReminders">
              {{ t("missions.planRemindersCta") }}
            </BaseButton>
          </div>

          <div v-if="timelineUntimedItems.length" class="timelineUntimed">
            <p>{{ t("missions.timeline.untimedTitle") }}</p>
            <div class="timelineUntimedItems">
              <button v-for="mission in timelineUntimedItems" :key="mission.mission_id" type="button"
                class="timelineUntimedItem"
                :class="[normalizedMissionIntensity(mission), normalizedMissionStatus(mission.status), { active: isTimelineMissionSelected(mission) }]"
                @click="selectTimelineMission(mission)">
                <span class="timelineMiniMarker timelineMarkerButton" :class="missionMarkerClasses(mission)"
                  aria-hidden="true">
                  <span class="timelineMarkerShape"></span>
                </span>
                <strong>{{ mission.title }}</strong>
                <span v-if="missionXpMeta(mission)" class="timelineMarkerXp" :class="missionXpMeta(mission).state">
                  {{ missionXpMeta(mission).label }}
                </span>
                <span v-for="chip in missionMetadataChips(mission)" :key="chip.key" class="timelineMetaPill"
                  :class="chip.type">
                  {{ chip.label }}
                </span>
              </button>
            </div>
          </div>

          <div class="timelineStage">
            <div class="timelineColumn">
              <div class="timelineRail" :class="{ compact: timelineIsSparse }"
                :aria-label="t('missions.timeline.title')">
                <div class="timelineResetLabels">
                  <span>{{ t("missions.timeline.startLabel", { time: timelineBounds.startLabel }) }}</span>
                  <span>{{ t("missions.timeline.resetLabel", { time: timelineBounds.endLabel }) }}</span>
                </div>
                <div class="timelineTrack">
                  <div v-for="guide in timelineGuides" :key="guide.key" class="timelineGuide"
                    :style="{ top: `${guide.position}%` }">
                    <span class="timelineGuideLine"></span>
                    <span class="timelineGuideLabel">{{ guide.label }}</span>
                  </div>
                  <div class="timelineNow" :style="{ top: `${timelineNowPosition}%` }">
                    <span>{{ timelineNowLabel }}</span>
                  </div>
                  <div v-for="cluster in timelineClusters" :key="cluster.key" class="timelineCluster"
                    :class="{ multi: cluster.items.length > 1 }" :style="{ top: `${cluster.position}%` }">





                    <button type="button" class="timelineMarkerButton" :class="[
                      cluster.markerTypeClass,
                      cluster.markerStatusClass,
                      {
                        active: cluster.items.some((item) => isTimelineMissionSelected(item.mission)),
                        multi: cluster.items.length > 1,
                        nearReset: cluster.nearReset,
                      },
                    ]" :aria-label="cluster.ariaLabel" @click="selectTimelineCluster(cluster)">
                      <span class="timelineMarkerShape" aria-hidden="true">
                        <span v-if="cluster.items.length > 1" class="timelineMarkerCount">
                          {{ cluster.items.length }}
                        </span>
                      </span>
                    </button>


                    <span v-if="cluster.items.length > 1" class="timelineClusterTypes" aria-hidden="true">
                      <span v-for="item in cluster.items" :key="item.key"
                        class="timelineClusterMiniMarker timelineMarkerButton"
                        :class="missionMarkerClasses(item.mission)">
                        <span class="timelineMarkerShape"></span>
                      </span>
                    </span>


                    <span v-if="cluster.xp" class="timelineMarkerXp"
                      :class="[cluster.xp.state, { nearReset: cluster.nearReset }]">
                      {{ cluster.xp.label }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <aside class="timelineSidePanel">
              <div class="timelineSupport">
                <div class="timelineSupportHead">
                  <div>
                    <p class="eyebrow compact">{{ t("missions.otherEyebrow") }}</p>
                    <h2>{{ t("missions.otherTitle") }}</h2>
                    <p v-if="isTodaySaved" class="otherMissionContext">
                      {{ t("missions.optionalOtherContext") }}
                    </p>
                  </div>
                  <BaseButton variant="secondary" @click="hideMissionStatusDetails">
                    {{ t("missions.hideOtherMissions") }}
                  </BaseButton>
                </div>
                <div class="timelineLegend" :aria-label="t('missions.statusChipsLabel')">
                  <span class="timelineLegendItem main">
                    <i></i>{{ t("missions.typeChips.main") }}
                  </span>
                  <span class="timelineLegendItem tiny">
                    <i></i>{{ t("missions.typeChips.tiny") }}
                  </span>
                  <span class="timelineLegendItem bonus">
                    <i></i>{{ t("missions.typeChips.bonus") }}
                  </span>
                  <span class="timelineLegendStatus pending">
                    <i></i>{{ t("missions.status.pending") }}
                  </span>
                  <span class="timelineLegendStatus done">
                    <i></i>{{ t("missions.status.done") }}
                  </span>
                  <span class="timelineLegendStatus remind_later">
                    <i></i>{{ t("missions.status.remind_later") }}
                  </span>
                  <span class="timelineLegendStatus skipped">
                    <i></i>{{ t("missions.status.skipped") }}
                  </span>
                </div>
              </div>

              <div class="timelineMissionRows">
                <template v-for="mission in timelineDetailMissions" :key="mission.mission_id">
                  <button type="button" class="timelineMissionRow"
                    :class="[normalizedMissionStatus(mission.status), { active: isTimelineMissionSelected(mission) }]"
                    @click="selectTimelineMission(mission)">
                    <span class="timelineMiniMarker timelineMarkerButton" :class="missionMarkerClasses(mission)"
                      aria-hidden="true">
                      <span class="timelineMarkerShape"></span>
                    </span>
                    <strong>{{ mission.title }}</strong>
                    <span v-if="missionXpMeta(mission)" class="timelineMarkerXp" :class="missionXpMeta(mission).state">
                      {{ missionXpMeta(mission).label }}
                    </span>
                    <span v-for="chip in missionMetadataChips(mission)" :key="chip.key" class="timelineMetaPill"
                      :class="chip.type">
                      {{ chip.label }}
                    </span>
                    <span v-if="timelineMissionTimeLabel(mission)" class="timelineMissionTime">
                      {{ timelineMissionTimeLabel(mission) }}
                    </span>
                  </button>

                  <article v-if="isTimelineMissionSelected(mission)" :id="`timeline-mission-${mission.mission_id}`"
                    class="timelineDetail missionItem" :class="[normalizedMissionStatus(mission.status)]">
                    <div>
                      <div class="timelineDetailHero">
                        <span class="timelineDetailMarker timelineMarkerButton" :class="missionMarkerClasses(mission)"
                          aria-hidden="true">
                          <span class="timelineMarkerShape"></span>
                        </span>
                        <div>
                          <div class="missionChips" :aria-label="t('missions.statusChipsLabel')">
                            <span v-for="chip in missionChips(mission)" :key="chip.key" class="missionChip"
                              :class="chip.type">
                              {{ chip.label }}
                            </span>
                            <span v-if="missionXpMeta(mission)" class="missionChip xp"
                              :class="missionXpMeta(mission).state">
                              {{ missionXpMeta(mission).label }}
                            </span>
                            <span v-for="chip in missionMetadataChips(mission)" :key="chip.key" class="missionChip"
                              :class="chip.type">
                              {{ chip.label }}
                            </span>
                          </div>
                          <p class="missionMeta">
                            {{ mission.challenge_name }} · {{ missionStatusLabel(mission) }}
                          </p>
                        </div>
                      </div>
                      <h3>{{ mission.title }}</h3>
                      <small v-if="missionParentCopy(mission)" class="missionRelationCopy">
                        {{ missionParentCopy(mission) }}
                      </small>
                      <p>{{ mission.description }}</p>
                      <small v-if="missionStatusCopy(mission)" class="missionStatusCopy">
                        {{ missionStatusCopy(mission) }}
                      </small>
                      <small v-if="reminderDeliveryMeta(mission)" class="reminderDeliveryChip"
                        :class="reminderDeliveryMeta(mission).state">
                        {{ reminderDeliveryMeta(mission).label }}
                      </small>
                    </div>

                    <div v-if="showMissionItemActions(mission)" class="missionActions">
                      <BaseButton variant="primary" :loading="busyId === mission.mission_id && busyAction === 'done'"
                        :disabled="missionHasStatus(mission, 'done')" @click="markDone(mission)">
                        <img v-if="missionActionIcon('done')" :src="missionActionIcon('done')" alt=""
                          class="missionActionIcon" aria-hidden="true" />
                        {{ t("missions.doneCta") }}
                      </BaseButton>

                      <BaseButton variant="secondary"
                        :loading="busyId === mission.mission_id && busyAction === 'remind'"
                        :disabled="missionHasStatus(mission, 'done')" @click="remindLater(mission)">
                        <img v-if="missionActionIcon('remindLater')" :src="missionActionIcon('remindLater')" alt=""
                          class="missionActionIcon" aria-hidden="true" />
                        {{ missionHasStatus(mission, "remind_later") ? t("missions.editReminder") :
                          t("missions.remindLater") }}
                      </BaseButton>

                      <BaseButton variant="secondary" :loading="busyId === mission.mission_id && busyAction === 'skip'"
                        :disabled="missionHasStatus(mission, 'done', 'skipped')" @click="skipMission(mission)">
                        <img v-if="missionActionIcon('skip')" :src="missionActionIcon('skip')" alt=""
                          class="missionActionIcon" aria-hidden="true" />
                        {{ missionHasStatus(mission, "skipped") ? t("missions.skipped") : t("missions.skip") }}
                      </BaseButton>

                      <BaseButton v-if="shouldShowMissionItemTinyAction(mission)" variant="secondary"
                        @click="focusTinyMissionVariant(mission)">
                        <img v-if="missionActionIcon('makeSmaller')" :src="missionActionIcon('makeSmaller')" alt=""
                          class="missionActionIcon" aria-hidden="true" />
                        {{ t("missions.ringoActions.tryTinyVersion") }}
                      </BaseButton>

                      <BaseButton v-if="shouldShowFullVersionAction(mission)" variant="secondary"
                        @click="focusMainMissionVariant(mission)">
                        <img v-if="missionActionIcon('makeBigger')" :src="missionActionIcon('makeBigger')" alt=""
                          class="missionActionIcon" aria-hidden="true" />
                        {{ t("missions.ringoActions.useFullVersion") }}
                      </BaseButton>
                    </div>

                    <div v-if="isReminderPanelOpen(mission)" class="remindOptionsPanel">
                      <p>{{ t("missions.remindOptions.prompt") }}</p>
                      <div class="remindOptions">
                        <BaseButton v-for="option in reminderOptions" :key="option.key" variant="secondary"
                          :loading="isReminderOptionLoading(mission, option.key)"
                          :disabled="busyAction === 'remind' && busyId === mission.mission_id"
                          @click="selectReminderOption(mission, option)">
                          {{ option.label }}
                        </BaseButton>
                        <BaseButton variant="secondary" :loading="isReminderOptionLoading(mission, 'ringo')"
                          :disabled="busyAction === 'remind' && busyId === mission.mission_id"
                          @click="planMissionReminder(mission)">
                          {{ t("missions.remindOptions.ringoPick") }}
                        </BaseButton>
                        <BaseButton variant="secondary"
                          :disabled="busyAction === 'remind' && busyId === mission.mission_id"
                          @click="openCustomReminderTime(mission)">
                          {{ t("missions.remindOptions.customTime") }}
                        </BaseButton>
                        <BaseButton variant="secondary" @click="closeReminderPanel">
                          {{ t("missions.backToMissionActions") }}
                        </BaseButton>
                      </div>
                      <div v-if="isCustomReminderPanelOpen(mission)" class="customReminderPanel">
                        <label :for="`custom-reminder-${mission.mission_id}`">
                          {{ t("missions.remindOptions.customPrompt") }}
                        </label>
                        <div class="customReminderControls">
                          <input :id="`custom-reminder-${mission.mission_id}`" v-model="customReminderTime"
                            type="time" />
                          <BaseButton variant="primary" :loading="isReminderOptionLoading(mission, 'custom')"
                            :disabled="busyAction === 'remind' && busyId === mission.mission_id"
                            @click="selectCustomReminderTime(mission)">
                            {{ t("missions.remindOptions.setCustom") }}
                          </BaseButton>
                        </div>
                        <small>{{ t("missions.remindOptions.customHelp") }}</small>
                      </div>
                    </div>

                    <div v-if="isSkipReasonPanelOpen(mission)" class="skipReasonPanel">
                      <p>{{ t("missions.skipReasons.prompt") }}</p>
                      <div class="skipReasons">
                        <BaseButton v-for="reason in skipReasonOptions" :key="reason.key" variant="secondary"
                          :loading="isSkipReasonLoading(mission, reason.key)"
                          :disabled="busyAction === 'skip' && busyId === mission.mission_id"
                          @click="selectSkipReason(mission, reason)">
                          {{ reason.label }}
                        </BaseButton>
                        <BaseButton variant="secondary" @click="closeSkipReasonPanel">
                          {{ t("missions.backToMissionActions") }}
                        </BaseButton>
                      </div>
                    </div>
                  </article>
                </template>

                <div v-if="!timelineDetailMissions.length" class="timelineDetailPlaceholder">
                  <p class="eyebrow compact">{{ t("missions.timeline.eyebrow") }}</p>
                  <h3>{{ t("missions.timeline.selectTitle") }}</h3>
                  <p>{{ t("missions.timeline.selectBody") }}</p>
                </div>
              </div>
            </aside>
          </div>

        </div>

      </div>

      <div v-else class="missionListHead collapsedMissionStatus">
        <div>
          <p class="eyebrow compact">{{ t("missions.otherEyebrow") }}</p>
          <h2>{{ t("missions.otherTitle") }}</h2>
          <p class="otherMissionHint">
            {{ t(isTodaySaved ? "missions.optionalOtherHint" : "missions.otherHint", { count: otherMissions.length }) }}
          </p>
        </div>
        <BaseButton variant="secondary" @click="showOtherMissions = true">
          {{ t("missions.showOtherMissions", { count: otherMissions.length }) }}
        </BaseButton>
      </div>
    </BaseCard>

    <div v-else-if="showMissionStatusToggle" class="missionStatusToggle">
      <BaseButton variant="secondary" @click="missionStatusExpanded = true">
        {{ t("missions.showMissionStatus") }}
      </BaseButton>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";
import RingoCoach from "@/components/ringo/RingoCoach.vue";
import RingoRewardSequence from "@/components/ringo/RingoRewardSequence.vue";
import DailyMomentumBar from "@/components/missions/DailyMomentumBar.vue";
import ExplorePathsPanel from "@/components/missions/ExplorePathsPanel.vue";
import MissionContextPanel from "@/components/missions/MissionContextPanel.vue";
import PathSelection from "@/components/missions/PathSelection.vue";
import RemainingMissionExplorer from "@/components/missions/RemainingMissionExplorer.vue";
import { resolveRingoSprite } from "@/constants/ringoSprites";
import {
  localizeChallenge,
  localizePath,
  localizeMissionList,
  localizeRingoState,
} from "@/lib/ringoContentLocalization";
import {
  buildMissionPathGroups,
  resolvePathIcon,
} from "@/utils/missionMomentumUtils";
import { resolveActionIcon } from "@/utils/actionIconUtils";
import {
  buildRewardDelta,
  buildMissionCompletionRewardSteps,
  buildRewardSnapshot,
} from "@/utils/rewardSequenceBuilder";


// import missionDoneIcon from '../../assets/icons/actions/icon-action-continue.svg';
// import missionRemindIcon from '../../assets/icons/actions/icon-action-remind.svg';
// import missionSkipIcon from '../../assets/icons/actions/icon-action-skip.svg';


const { locale, t } = useI18n();
const router = useRouter();
const props = defineProps({
  firstRunFocus: { type: Boolean, default: false },
  focusModeActive: { type: Boolean, default: false },
  stats: { type: Object, default: null },
});

const emit = defineEmits(["checked-in", "loaded", "first-run-complete", "focus-state-change", "show-dashboard"]);

const loading = ref(true);
const error = ref("");
const date = ref("");
const ringo = ref(null);
const ringoGuidance = ref(null);
const missions = ref([]);
const pathCatalog = ref([]);
const busyId = ref(null);
const busyAction = ref("");
const notice = ref("");
const noticeType = ref("success");
const telegramPromptRef = ref(null);
const dismissedCoachState = ref("");
const interactionNarrative = ref(null);
const completionNarrative = ref(null);
const manualFocusMissionId = ref(null);
const showOtherMissions = ref(true);
const missionStatusExpanded = ref(false);
const restModeActive = ref(false);
const optionalExplorerExpanded = ref(false);
const selectedOptionalExplorerMissionId = ref(null);
const selectedMomentumPathId = ref("");
const explorePathsPanelOpen = ref(false);
const selectedTimelineMissionId = ref(null);
const reminderPanelMissionId = ref(null);
const busyReminderOption = ref("");
const customReminderPanelMissionId = ref(null);
const customReminderTime = ref("");
const skipReasonPanelMissionId = ref(null);
const busySkipReason = ref("");
const planningReminders = ref(false);
const rewardSequenceSteps = ref([]);
const rewardSequenceSprite = ref("celebration");
const optionalNextSuppressed = ref(false);
const optionalSuggestionRequested = ref(false);
const revealedTinyMissionIds = ref(new Set());
const telegramSettings = ref({
  connected: false,
  reminders_enabled: false,
  bot_username: "",
  bot_link: "",
});
const telegramReminderPrompt = ref(null);
const telegramConnectCode = ref(null);
const telegramPromptBusy = ref(false);
const telegramPromptError = ref("");

const SUPPORTED_GUIDANCE_ACTIONS = new Set([
  "start",
  "remind_later",
  "make_smaller",
  "too_tired",
  "skip_today",
]);

const REMINDER_OPTION_KEYS = [
  "fifteenMinutes",
  "oneHour",
  "evening",
  "tonight",
];

const SKIP_REASON_OPTIONS = [
  { key: "tooTired", reason: "too_tired" },
  { key: "noTime", reason: "no_time" },
  { key: "tooHard", reason: "too_hard" },
  { key: "notRelevant", reason: "not_relevant" },
  { key: "dontLike", reason: "disliked" },
  { key: "other", reason: "other" },
  { key: "withoutReason", reason: null },
];

const SUPPORTED_AGENDA_ACTIONS = new Set([
  "due_reminder",
  "upcoming_reminder",
  "primary_mission",
  "optional_mission",
  "skipped_optional",
  "done_for_today",
]);

const MISSION_AGENDA_ACTIONS = new Set([
  "due_reminder",
  "upcoming_reminder",
  "primary_mission",
  "optional_mission",
  "skipped_optional",
]);

const showPathSelection = computed(() => {
  return ["new_user_no_path", "path_selected_no_challenge"].includes(ringo.value?.state);
});

const showCoach = computed(() => {
  if (
    interactionNarrative.value
    || completionNarrative.value
    || finishedForTodayNarrative.value
    || dailySummaryNarrative.value
    || agendaNarrative.value
    || guidanceRingo.value
  ) return true;
  return ringo.value?.state && ringo.value.state !== dismissedCoachState.value;
});

const localizedMissions = computed(() => {
  return localizeMissionList(missions.value, locale.value);
});

const localizedRingo = computed(() => {
  return localizeRingoState(ringo.value, localizedMissions.value, locale.value);
});

const guidanceRingo = computed(() => ringoGuidance.value?.ringo || null);

const guidanceAgenda = computed(() => {
  const agenda = ringoGuidance.value?.agenda;
  if (!agenda || typeof agenda !== "object") return null;
  if (!SUPPORTED_AGENDA_ACTIONS.has(agenda.next_action_type)) return null;

  return agenda;
});

const guidanceRingoDay = computed(() => {
  const ringoDay = ringoGuidance.value?.ringo_day;
  return ringoDay && typeof ringoDay === "object" ? ringoDay : null;
});

const telegramConnected = computed(() => Boolean(telegramSettings.value?.connected));

const telegramRemindersEnabled = computed(() => Boolean(telegramSettings.value?.reminders_enabled));

const telegramConnectLink = computed(() => {
  const code = telegramConnectCode.value?.code;
  if (!code) return telegramConnectCode.value?.bot_link || "";

  const providedLink = telegramConnectCode.value?.bot_link;
  if (providedLink && providedLink.includes("?start=")) return providedLink;

  const baseLink = providedLink || telegramSettings.value?.bot_link;
  if (!baseLink) {
    const username = telegramConnectCode.value?.bot_username || telegramSettings.value?.bot_username;
    return username ? `https://t.me/${String(username).replace(/^@/, "")}?start=${encodeURIComponent(code)}` : "";
  }

  const separator = baseLink.includes("?") ? "&" : "?";
  return `${baseLink}${separator}start=${encodeURIComponent(code)}`;
});

const preferLocalizedRingo = computed(() => {
  return String(locale.value || "").toLowerCase().startsWith("fa");
});

const backendCoachNarrative = computed(() => {
  const source = guidanceRingo.value || localizedRingo.value || {};

  return {
    message: source.message || "",
    mood: source.sprite_key || source.mood || source.sprite || "idle",
  };
});

const optionalNextNarrative = computed(() => {
  if (!isTodaySaved.value || !optionalNextMission.value) return null;

  return {
    message: t("missions.narrative.optionalNext", { mission: optionalNextMission.value.title }),
    mood: "happy",
  };
});

const dueReminderNarrative = computed(() => {
  if (!dueReminderFocusActive.value) return null;

  return {
    message: t("missions.narrative.optionalSelectedDueReminder"),
    mood: "thinking",
  };
});

const finishedForTodayNarrative = computed(() => {
  if (!optionalNextSuppressed.value || !isTodaySaved.value) return null;

  return doneForTodayAgendaNarrative();
});

const dailySummaryNarrative = computed(() => {
  if (!isTodaySaved.value || !localizedMissions.value.length) return null;
  if (showOptionalExplorerPrompt.value) return null;

  const summary = dailySummary.value;
  const nearestReminder = summary.reminded[0] || null;
  const reminderTime = formattedReminderLabel(nearestReminder?.reminder_at || guidanceAgenda.value?.next_reminder_at);
  const reminderSummaryTime = formattedReminderSummaryLabel(
    nearestReminder?.reminder_at || guidanceAgenda.value?.next_reminder_at,
  );
  const params = {
    done: summary.done.length,
    reminded: summary.reminded.length,
    skipped: summary.skipped.length,
    mission: nearestReminder?.title || t("missions.fallbackMission"),
    time: reminderTime,
    summaryTime: reminderSummaryTime,
  };
  const facts = [];

  if (summary.bonusDone.length) {
    facts.push(t("missions.dailySummary.bonusCompletedFact"));
  } else if (summary.done.length > 1) {
    facts.push(t("missions.dailySummary.multipleDoneFact", params));
  }

  if (nearestReminder) {
    const reminderDue = isReminderDue(nearestReminder);
    const reminderKey = reminderDue
      ? summary.reminded.length > 1
        ? "missions.dailySummary.dueReminderMultiple"
        : "missions.dailySummary.dueReminder"
      : summary.reminded.length > 1
        ? "missions.dailySummary.upcomingReminderMultiple"
        : "missions.dailySummary.upcomingReminder";
    facts.push(t(reminderKey, params));
  }

  if (summary.skipped.length) {
    facts.push(t("missions.dailySummary.skippedFact", params));
  }

  if (facts.length) {
    return {
      message: [
        t("missions.dailySummary.safePrefix"),
        ...facts,
      ].join(" "),
      mood: nearestReminder && isReminderDue(nearestReminder)
        ? "thinking"
        : summary.bonusDone.length || summary.done.length > 1
          ? "proud"
          : summary.skipped.length
            ? "concerned"
            : "calm",
    };
  }

  if (summary.bonusAvailable.length) {
    if (summary.tinyDone.length && !summary.mainDone.length) {
      return {
        message: t("missions.dailySummary.tinySafeWithBonusAvailable", params),
        mood: "sleeping",
      };
    }

    return {
      message: t("missions.dailySummary.bonusAvailable", params),
      mood: "happy",
    };
  }

  return {
    message: t("missions.dailySummary.allDone", params),
    mood: "sleeping",
  };
});

const agendaNarrative = computed(() => {
  const agenda = guidanceAgenda.value;
  if (!agenda) return null;
  const hasMissionTarget = agenda.next_mission_id !== null && agenda.next_mission_id !== undefined;
  const hasMissionCounts = Number(agenda.pending_count || 0)
    + Number(agenda.reminded_count || 0)
    + Number(agenda.skipped_count || 0)
    + Number(agenda.done_count || 0) > 0;

  if (agenda.next_action_type !== "done_for_today" && !hasMissionTarget) return null;
  if (agenda.next_action_type === "done_for_today" && !agenda.today_saved && !hasMissionCounts) return null;

  const mission = missionForAgenda(agenda);
  const usesMissionTarget = MISSION_AGENDA_ACTIONS.has(agenda.next_action_type);
  const missionIsReachable = mission && isAgendaMissionReachable(mission, agenda.next_action_type);

  if (optionalNextSuppressed.value && agenda.today_saved) {
    return doneForTodayAgendaNarrative();
  }

  if (
    agenda.today_saved
    && agenda.next_action_type === "optional_mission"
    && !optionalSuggestionRequested.value
  ) {
    return {
      message: t("missions.agendaNarrative.optionalPrompt"),
      mood: "sleeping",
    };
  }

  if (usesMissionTarget && !missionIsReachable) {
    if (agenda.next_action_type === "skipped_optional") {
      return {
        message: t("missions.agendaNarrative.skippedOptionalGeneric"),
        mood: "concerned",
      };
    }

    if (agenda.today_saved) {
      return doneForTodayAgendaNarrative();
    }

    return null;
  }

  const missionTitle = mission?.title || t("missions.fallbackMission");
  const reminderTime = formattedReminderTime(agenda.next_reminder_at);
  const params = {
    mission: missionTitle,
    time: reminderTime,
  };

  if (agenda.next_action_type === "due_reminder") {
    return {
      message: t(
        agenda.today_saved
          ? "missions.agendaNarrative.dueReminderSaved"
          : "missions.agendaNarrative.dueReminder",
        params,
      ),
      mood: agenda.today_saved ? "happy" : "thinking",
    };
  }

  if (agenda.next_action_type === "upcoming_reminder") {
    return {
      message: reminderTime
        ? t(
          agenda.today_saved
            ? "missions.agendaNarrative.upcomingReminderSavedWithTime"
            : "missions.agendaNarrative.upcomingReminderWithTime",
          params,
        )
        : t(
          agenda.today_saved
            ? "missions.agendaNarrative.upcomingReminderSaved"
            : "missions.agendaNarrative.upcomingReminder",
          params,
        ),
      mood: agenda.today_saved ? "happy" : "calm",
    };
  }

  if (agenda.next_action_type === "primary_mission") {
    return {
      message: t("missions.agendaNarrative.primaryMission", params),
      mood: "focus",
    };
  }

  if (agenda.next_action_type === "optional_mission") {
    return {
      message: t("missions.agendaNarrative.optionalMission", params),
      mood: "happy",
    };
  }

  if (agenda.next_action_type === "skipped_optional") {
    return {
      message: t("missions.agendaNarrative.skippedOptional", params),
      mood: "concerned",
    };
  }

  if (agenda.next_action_type === "done_for_today") {
    return doneForTodayAgendaNarrative();
  }

  return null;
});

const coachNarrative = computed(() => {
  return dueReminderNarrative.value
    || interactionNarrative.value
    || finishedForTodayNarrative.value
    || dailySummaryNarrative.value
    || completionNarrative.value
    || agendaNarrative.value
    || optionalNextNarrative.value
    || backendCoachNarrative.value
    || {
    message: t("ringoCoach.fallbackMessage"),
    mood: "idle",
  };
});

const coachMessage = computed(() => {
  return coachNarrative.value?.message || t("ringoCoach.fallbackMessage");
});

const coachSprite = computed(() => {
  return coachNarrative.value?.mood || "idle";
});

const hasRingoGuidance = computed(() => !!guidanceRingo.value);

const coachPrimaryAction = computed(() => {
  if (hasRingoGuidance.value || isTodaySaved.value || focusMission.value) return null;

  return localizedRingo.value?.primary_action || null;
});

const coachSecondaryAction = computed(() => {
  if (hasRingoGuidance.value || isTodaySaved.value || focusMission.value) return null;

  return localizedRingo.value?.secondary_action || null;
});

const guidanceMission = computed(() => {
  const mission = ringoGuidance.value?.mission;
  if (!mission?.mission_id) return mission || null;

  const currentMission = localizedMissions.value.find((item) => {
    return sameMissionId(item.mission_id, mission.mission_id);
  });

  return currentMission ? { ...mission, ...currentMission } : mission;
});

const ringoPrimaryActionMission = computed(() => {
  const action = localizedRingo.value?.primary_action;
  if (action?.type !== "mission" || !action.mission_id) return null;

  return localizedMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, action.mission_id);
  }) || null;
});

const dueReminderMission = computed(() => {
  if (guidanceAgenda.value?.next_action_type === "due_reminder") {
    const agendaMission = missionForAgenda(guidanceAgenda.value);
    if (agendaMission) return agendaMission;
  }

  return sortReminderMissions(
    deferredMissions.value.filter((mission) => isReminderDue(mission)),
  )[0] || null;
});

const dueReminderFocusActive = computed(() => Boolean(dueReminderMission.value));

const pendingMissions = computed(() => {
  return autoFocusableMissionRepresentatives.value.filter((mission) => missionHasStatus(mission, "pending"));
});

const deferredMissions = computed(() => {
  return autoFocusableMissionRepresentatives.value.filter((mission) => missionHasStatus(mission, "remind_later"));
});

const skippedMissions = computed(() => {
  return autoFocusableMissionRepresentatives.value.filter((mission) => missionHasStatus(mission, "skipped"));
});

const manualFocusMission = computed(() => {
  if (!manualFocusMissionId.value) return null;

  return localizedMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, manualFocusMissionId.value);
  }) || null;
});

const activeInteractionMission = computed(() => {
  const missionId = manualFocusMissionId.value
    || reminderPanelMissionId.value
    || skipReasonPanelMissionId.value
    || busyId.value;

  if (!missionId) return null;

  return localizedMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, missionId);
  }) || null;
});

const focusMission = computed(() => {
  return activeInteractionMission.value
    || dueReminderMission.value
    || guidanceMission.value
    || ringoPrimaryActionMission.value
    || primaryReminderMission()
    || pendingMissions.value[0]
    || skippedMissions.value[0]
    || deferredMissions.value[0]
    || localizedMissions.value[0]
    || null;
});

const focusMissionIntensity = computed(() => buildMissionIntensityMeta(focusMission.value, {
  optionalContext: isTodaySaved.value && !missionHasStatus(focusMission.value, "done"),
}));

const rawOtherMissions = computed(() => {
  return localizedMissions.value;
});

const mainDoneMissionIds = computed(() => {
  return new Set(
    localizedMissions.value
      .filter((mission) => normalizedMissionIntensity(mission) === "main" && missionHasStatus(mission, "done"))
      .map((mission) => String(mission.mission_id)),
  );
});

const tinyDoneParentMissionIds = computed(() => {
  return new Set(
    localizedMissions.value
      .filter((mission) => normalizedMissionIntensity(mission) === "tiny" && missionHasStatus(mission, "done"))
      .map((mission) => String(mission.parent_mission_id || ""))
      .filter(Boolean),
  );
});

const effectiveMissionRepresentatives = computed(() => {
  const representatives = [];
  const groups = new Map();

  localizedMissions.value.forEach((mission) => {
    const rootId = missionGroupRootId(mission);
    if (!rootId) return;

    if (!groups.has(rootId)) groups.set(rootId, []);
    groups.get(rootId).push(mission);
  });

  groups.forEach((items) => {
    const mainMission = items.find((mission) => normalizedMissionIntensity(mission) === "main") || null;
    const tinyMissions = items.filter((mission) => normalizedMissionIntensity(mission) === "tiny");
    const bonusMissions = items.filter((mission) => normalizedMissionIntensity(mission) === "bonus");
    const focusedMission = items.find((mission) => {
      return sameMissionId(mission.mission_id, manualFocusMissionId.value);
    }) || null;
    const effectiveTiny = tinyMissions.find((mission) => {
      return missionHasStatus(mission, "remind_later", "done", "skipped");
    }) || tinyMissions.find((mission) => {
      return isTinyMissionRevealed(mission) && missionHasStatus(mission, "pending");
    }) || null;
    const meaningfulTiny = tinyMissions.find((mission) => {
      return missionHasStatus(mission, "remind_later", "done", "skipped");
    }) || null;

    if (focusedMission && !missionHasStatus(focusedMission, "locked")) {
      if (normalizedMissionIntensity(focusedMission) === "tiny" || !meaningfulTiny) {
        representatives.push(focusedMission);
        if (mainMission && sameMissionId(focusedMission.mission_id, mainMission.mission_id) && missionHasStatus(mainMission, "done")) {
          bonusMissions
            .filter((mission) => missionHasStatus(mission, "pending", "done", "remind_later", "skipped"))
            .forEach((mission) => representatives.push(mission));
        }
        return;
      }
    }

    if (mainMission && missionHasStatus(mainMission, "done")) {
      representatives.push(mainMission);
      bonusMissions
        .filter((mission) => missionHasStatus(mission, "pending", "done", "remind_later", "skipped"))
        .forEach((mission) => representatives.push(mission));
      return;
    }

    if (meaningfulTiny) {
      representatives.push(meaningfulTiny);
      if (missionHasStatus(meaningfulTiny, "done")) {
        bonusMissions
          .filter((mission) => missionHasStatus(mission, "pending", "done", "remind_later", "skipped"))
          .forEach((mission) => representatives.push(mission));
      }
      return;
    }

    if (mainMission && missionHasStatus(mainMission, "remind_later", "done", "skipped")) {
      representatives.push(mainMission);
      if (missionHasStatus(mainMission, "done")) {
        bonusMissions
          .filter((mission) => missionHasStatus(mission, "pending", "done", "remind_later", "skipped"))
          .forEach((mission) => representatives.push(mission));
      }
      return;
    }

    if (mainMission) {
      representatives.push(mainMission);
      return;
    }

    if (effectiveTiny) {
      representatives.push(effectiveTiny);
      return;
    }

    const fallbackMission = items.find((mission) => {
      return missionHasStatus(mission, "remind_later", "done", "pending", "skipped");
    });

    if (fallbackMission) representatives.push(fallbackMission);
  });

  return representatives;
});

const autoFocusableMissionRepresentatives = computed(() => {
  return effectiveMissionRepresentatives.value.filter((mission) => {
    if (normalizedMissionIntensity(mission) !== "bonus") return true;
    if (!missionHasStatus(mission, "pending")) return true;
    if (!isTodaySaved.value) return true;

    const parentId = String(mission.parent_mission_id || "");
    if (!parentId) return true;
    if (mainDoneMissionIds.value.has(parentId)) return true;

    return !tinyDoneParentMissionIds.value.has(parentId);
  });
});

const curatedOtherMissions = computed(() => {
  const visibleMissionIds = new Set(effectiveMissionRepresentatives.value.map((mission) => String(mission.mission_id)));

  return rawOtherMissions.value.filter((mission) => {
    return visibleMissionIds.has(String(mission.mission_id)) && shouldShowOtherMission(mission);
  });
});

const showOtherMissionList = computed(() => {
  if (loading.value || error.value || !otherMissions.value.length) return false;

  return true;
});

const safeOptionalMissions = computed(() => {
  const agendaOptionalMissionId = guidanceAgenda.value?.next_action_type === "optional_mission"
    ? guidanceAgenda.value.next_mission_id
    : null;

  const candidates = effectiveMissionRepresentatives.value.filter((mission) => {
    if (!missionHasStatus(mission, "pending")) return false;
    if (isFocusMissionRendered() && sameMissionId(mission.mission_id, focusMission.value?.mission_id)) return false;
    if (isTodaySaved.value) {
      if (agendaOptionalMissionId && sameMissionId(mission.mission_id, agendaOptionalMissionId)) return true;
      if (normalizedMissionIntensity(mission) !== "bonus") return false;
      if (mission.parent_mission_id && !mainDoneMissionIds.value.has(String(mission.parent_mission_id))) return false;
    }

    return true;
  });

  if (!candidates.length) return [];

  const focusChallengeId = focusMission.value?.challenge_id;

  return [...candidates].sort((a, b) => {
    return optionalMissionRank(a, focusChallengeId) - optionalMissionRank(b, focusChallengeId);
  });
});

const optionalNextMission = computed(() => {
  if (!isTodaySaved.value || optionalNextSuppressed.value) return null;
  if (dueReminderFocusActive.value) return null;
  if (!optionalSuggestionRequested.value) return null;
  if (optionalExplorerExpanded.value || selectedOptionalExplorerMissionId.value) return null;

  return safeOptionalMissions.value[0] || null;
});

const optionalExplorerMissions = computed(() => {
  if (!isTodaySaved.value || optionalNextSuppressed.value) return [];

  return effectiveMissionRepresentatives.value
    .filter(shouldShowOptionalExplorerMission)
    .sort((a, b) => {
      const pathCompare = String(a.path_title || "").localeCompare(String(b.path_title || ""));
      if (pathCompare) return pathCompare;

      const challengeCompare = String(a.challenge_name || "").localeCompare(String(b.challenge_name || ""));
      if (challengeCompare) return challengeCompare;

      return optionalMissionRank(a, focusMission.value?.challenge_id) - optionalMissionRank(b, focusMission.value?.challenge_id);
    });
});

const optionalWorkAvailable = computed(() => {
  if (!isTodaySaved.value || optionalNextSuppressed.value) return false;

  return Boolean(
    safeOptionalMissions.value.length
    || optionalExplorerMissions.value.length
    || guidanceAgenda.value?.has_optional_work
  );
});

const optionalSuggestionAvailable = computed(() => {
  return Boolean(
    isTodaySaved.value
    && !optionalNextSuppressed.value
    && !dueReminderFocusActive.value
    && safeOptionalMissions.value.length
  );
});

const futureReminderCount = computed(() => {
  if (!isTodaySaved.value || optionalNextSuppressed.value) return 0;

  return optionalExplorerMissions.value.filter(isFutureReminder).length;
});

const showOptionalExplorerPrompt = computed(() => {
  return Boolean(
    isTodaySaved.value
    && !showDailyMomentumBar.value
    && !optionalNextMission.value
    && !optionalNextSuppressed.value
    && !dueReminderFocusActive.value
    && !optionalExplorerExpanded.value
    && !selectedOptionalExplorerMissionId.value
    && optionalWorkAvailable.value
  );
});

const selectedOptionalExplorerMission = computed(() => {
  if (!selectedOptionalExplorerMissionId.value) return null;

  return optionalExplorerMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, selectedOptionalExplorerMissionId.value);
  }) || null;
});

const showOptionalMissionExplorer = computed(() => {
  return Boolean(
    isTodaySaved.value
    && optionalExplorerExpanded.value
    && !dueReminderFocusActive.value
    && !selectedOptionalExplorerMission.value
    && !optionalNextSuppressed.value
    && optionalExplorerMissions.value.length
  );
});

const selectedOptionalExplorerBody = computed(() => {
  const mission = selectedOptionalExplorerMission.value;
  if (!mission) return t("missions.optionalExplorerSelectedBody");

  return t(selectedOptionalExplorerNarrativeKey(mission));
});

const showCompletedChoices = computed(() => {
  return Boolean(
    isTodaySaved.value
    && !showDailyMomentumBar.value
    && !dueReminderFocusActive.value
    && !optionalNextMission.value
    && !showOptionalExplorerPrompt.value
    && !showOptionalMissionExplorer.value
    && !selectedOptionalExplorerMission.value
  );
});

const otherMissions = computed(() => {
  return curatedOtherMissions.value.filter(shouldShowOtherMissionItem);
});

const missionStatusMissions = computed(() => otherMissions.value);

const selectedTimelineMission = computed(() => {
  if (!selectedTimelineMissionId.value) return null;

  return otherMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, selectedTimelineMissionId.value);
  }) || null;
});

const timelineBounds = computed(() => {
  const nextReset = parsedNextResetAt();
  const now = new Date();

  if (nextReset) {
    const start = new Date(nextReset.getTime() - (24 * 60 * 60 * 1000));

    return {
      start,
      end: nextReset,
      startLabel: formattedTimelineTime(start),
      endLabel: formattedTimelineTime(nextReset),
    };
  }

  const start = new Date(now);
  start.setHours(0, 0, 0, 0);
  const end = new Date(start);
  end.setDate(end.getDate() + 1);

  return {
    start,
    end,
    startLabel: formattedTimelineTime(start),
    endLabel: formattedTimelineTime(end),
  };
});

const timelineNowPosition = computed(() => {
  return timelinePositionForDate(new Date());
});

const timelineNowLabel = computed(() => {
  return t("missions.timeline.nowWithTime", { time: formattedTimelineTime(new Date()) });
});

const timelineGuides = computed(() => {
  const { start, end } = timelineBounds.value;
  const span = Math.max(end.getTime() - start.getTime(), 1);
  const guideCount = 8;

  return Array.from({ length: guideCount - 1 }, (_, index) => {
    const ratio = (index + 1) / guideCount;
    const timestamp = new Date(start.getTime() + (span * ratio));

    return {
      key: timestamp.toISOString(),
      position: ratio * 100,
      label: formattedTimelineTime(timestamp),
    };
  });
});

const timelineIsSparse = computed(() => {
  return timelineClusters.value.length <= 1;
});

const timelineTimedItems = computed(() => {
  return otherMissions.value
    .map((mission) => {
      const timestamp = missionTimelineTimestamp(mission);
      if (!timestamp) return null;

      return {
        key: `${mission.mission_id}-${timestamp.toISOString()}`,
        mission,
        timestamp,
        position: timelinePositionForDate(timestamp),
        timeLabel: formattedTimelineTime(timestamp),
        type: normalizedMissionIntensity(mission),
        status: normalizedMissionStatus(mission.status),
        meta: `${missionTypeLabel(mission)} · ${missionStatusLabel(mission)}`,
      };
    })
    .filter(Boolean)
    .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
});

const timelineClusters = computed(() => {
  const threshold = 5;

  return timelineTimedItems.value.reduce((clusters, item) => {
    const previous = clusters[clusters.length - 1];

    if (previous && Math.abs(item.position - previous.position) <= threshold) {
      const nextCluster = timelineClusterFromItems([...previous.items, item]);
      clusters.splice(clusters.length - 1, 1, nextCluster);
      return clusters;
    }

    clusters.push(timelineClusterFromItems([item]));

    return clusters;
  }, []);
});

const selectedTimelineClusterItems = computed(() => {
  if (!selectedTimelineMissionId.value) return [];

  const cluster = timelineClusters.value.find((item) => {
    return item.items.some((clusterItem) => {
      return sameMissionId(clusterItem.mission.mission_id, selectedTimelineMissionId.value);
    });
  });

  return cluster?.items || [];
});

const timelineDetailMissions = computed(() => {
  if (selectedTimelineClusterItems.value.length) {
    return selectedTimelineClusterItems.value.map((item) => item.mission);
  }

  return selectedTimelineMission.value ? [selectedTimelineMission.value] : [];
});

const timelineUntimedItems = computed(() => {
  const timedMissionIds = new Set(timelineTimedItems.value.map((item) => String(item.mission.mission_id)));

  return otherMissions.value.filter((mission) => {
    return !timedMissionIds.has(String(mission.mission_id));
  });
});

const plannableReminderCount = computed(() => {
  return otherMissions.value.filter((mission) => {
    return missionHasStatus(mission, "pending") && !mission.reminder_at;
  }).length;
});

const dailySummary = computed(() => {
  const effectiveMissions = effectiveMissionRepresentatives.value;
  const done = effectiveMissions.filter((mission) => missionHasStatus(mission, "done"));
  const mainDone = localizedMissions.value.filter((mission) => {
    return normalizedMissionIntensity(mission) === "main" && missionHasStatus(mission, "done");
  });
  const tinyDone = localizedMissions.value.filter((mission) => {
    return normalizedMissionIntensity(mission) === "tiny" && missionHasStatus(mission, "done");
  });
  const reminded = sortReminderMissions(
    effectiveMissions.filter((mission) => missionHasStatus(mission, "remind_later")),
  );
  const skipped = effectiveMissions.filter((mission) => missionHasStatus(mission, "skipped"));
  const bonusAvailable = otherMissions.value.filter((mission) => {
    return normalizedMissionIntensity(mission) === "bonus" && missionHasStatus(mission, "pending");
  });
  const bonusDone = localizedMissions.value.filter((mission) => {
    return normalizedMissionIntensity(mission) === "bonus" && missionHasStatus(mission, "done");
  });

  return {
    done,
    mainDone,
    tinyDone,
    reminded,
    skipped,
    bonusAvailable,
    bonusDone,
  };
});

const optionalNextMissionIntensity = computed(() => buildMissionIntensityMeta(optionalNextMission.value, {
  optionalContext: true,
}));

const missionContextCount = computed(() => {
  const contexts = new Set();

  localizedMissions.value.forEach((mission) => {
    const contextId = mission?.enrollment_id || mission?.challenge_id || mission?.path_id;
    if (contextId !== null && contextId !== undefined) {
      contexts.add(String(contextId));
    }
  });

  return contexts.size;
});

const allMissionsDone = computed(() => {
  return !!localizedMissions.value.length && localizedMissions.value.every((mission) => {
    return missionHasStatus(mission, "done");
  });
});

const detailsMission = computed(() => {
  if (optionalNextMission.value) return optionalNextMission.value;
  if (showFocusMissionCard.value) return focusMission.value;
  if (allMissionsDone.value && missionContextCount.value > 1) return null;

  return focusMission.value;
});

const showFocusMissionCard = computed(() => {
  return isFocusMissionRendered();
});

const missionGuide = computed(() => {
  if (!localizedMissions.value.length || !focusMission.value) return null;

  const complete = localizedMissions.value.every((mission) => missionHasStatus(mission, "done"));
  const hasSkipped = skippedMissions.value.length > 0;
  const hasDeferred = deferredMissions.value.length > 0;
  const hasPending = pendingMissions.value.length > 0;
  const context = {
    path: focusMission.value.path_title || t("missions.fallbackPath"),
    challenge: focusMission.value.challenge_name || t("missions.fallbackChallenge"),
    mission: focusMission.value.title,
  };

  if (complete) {
    return {
      complete: true,
      state: "complete",
      title: t("missions.guideCompleteTitle", context),
      body: t("missions.guideCompleteBody", context),
    };
  }

  if (isTodaySaved.value) {
    return {
      complete: true,
      state: "complete",
      title: t("missions.guideSavedTitle", context),
      body: t("missions.guideSavedBody", context),
    };
  }

  if (!hasPending && hasSkipped) {
    return {
      complete: false,
      state: "skipped",
      title: t("missions.guideSkippedTitle", context),
      body: t("missions.guideSkippedBody", context),
    };
  }

  if (!hasPending && hasDeferred) {
    return {
      complete: false,
      state: "reminder",
      title: t("missions.guideReminderTitle", context),
      body: t("missions.guideReminderBody", context),
    };
  }

  return {
    complete: false,
    state: "active",
    title: t("missions.guideTitle", context),
    body: t("missions.guideBody", context),
  };
});

const todaySavedLabel = computed(() => {
  if (!ringoGuidance.value?.progress?.today_saved) return "";

  return t("missions.todaySaved");
});

const isTodaySaved = computed(() => Boolean(ringoGuidance.value?.progress?.today_saved));

const dailyMomentumTodaySafe = computed(() => {
  const progress = ringoGuidance.value?.progress;
  if (progress && Object.prototype.hasOwnProperty.call(progress, "today_saved")) {
    return Boolean(progress.today_saved);
  }

  return localizedMissions.value.some((mission) => {
    return normalizedMissionIntensity(mission) !== "bonus" && missionHasStatus(mission, "done");
  });
});

const dailyMomentumStreakCount = computed(() => {
  const progressCount = Number(ringoGuidance.value?.progress?.current_streak);
  if (Number.isFinite(progressCount) && progressCount > 0) return progressCount;

  const missionWithStreak = localizedMissions.value.find((mission) => {
    return mission.challenge_streak
      || mission.challenge_current_streak
      || mission.current_streak;
  });
  const missionCount = Number(
    missionWithStreak?.challenge_streak
    ?? missionWithStreak?.challenge_current_streak
    ?? missionWithStreak?.current_streak,
  );

  return Number.isFinite(missionCount) && missionCount > 0 ? missionCount : null;
});

const pathMetadataById = computed(() => {
  const map = new Map();
  pathCatalog.value.forEach((path) => {
    if (path?.path_id === null || path?.path_id === undefined) return;
    map.set(String(path.path_id), path);
  });
  return map;
});

const dailyMomentumMissions = computed(() => {
  return effectiveMissionRepresentatives.value.map((mission) => {
    const metadata = pathMetadataById.value.get(String(mission.path_id || ""));
    if (!metadata) return mission;

    return {
      ...mission,
      path_icon: metadata.icon || mission.path_icon || "",
      path_color: metadata.color || mission.path_color || "",
      path_key: metadata.key || mission.path_key || "",
    };
  });
});

const dailyMomentumPathGroups = computed(() => {
  return buildMissionPathGroups(dailyMomentumMissions.value, {
    path: t("missions.fallbackPath"),
    challenge: t("missions.fallbackChallenge"),
  });
});

const dailyMomentumActivePathIds = computed(() => {
  return new Set(
    dailyMomentumPathGroups.value
      .flatMap((path) => [
        normalizedPathId(path.pathId || path.id),
        normalizedPathId(path.key),
      ])
      .filter(Boolean),
  );
});

const dailyMomentumUnexploredPaths = computed(() => {
  if (!pathCatalog.value.length) return [];
  const activePathIds = dailyMomentumActivePathIds.value;

  return pathCatalog.value.filter((path) => {
    const pathIds = [
      normalizedPathId(path?.path_id || path?.id),
      normalizedPathId(path?.key),
    ].filter(Boolean);
    return pathIds.length && !pathIds.some((pathId) => activePathIds.has(pathId));
  });
});

const dailyMomentumExplorePathItems = computed(() => {
  return dailyMomentumUnexploredPaths.value.map((path) => {
    const localizedPath = localizePath(path, locale.value) || path;
    const challengePreview = pathChallengePreview(path);

    return {
      ...localizedPath,
      color: localizedPath.color || path.color || "#f7d774",
      iconUrl: resolvePathIcon(localizedPath.icon || path.icon || path.key || ""),
      challengeCount: pathChallengeCount(path, challengePreview),
      challengePreview,
    };
  });
});

const showDailyMomentumExplorePaths = computed(() => {
  return dailyMomentumTodaySafe.value && dailyMomentumUnexploredPaths.value.length > 0;
});

const dailyMomentumAllPathsComplete = computed(() => {
  return dailyMomentumPathGroups.value.length > 0
    && dailyMomentumPathGroups.value.every((path) => Number(path?.stats?.percent || 0) >= 100);
});

const dailyMomentumNextAction = computed(() => {
  if (!dailyMomentumTodaySafe.value) {
    const mission = pendingMissions.value.find((item) => normalizedMissionIntensity(item) !== "bonus")
      || focusMission.value;

    return mission
      ? buildDailyMomentumAction("protect", mission)
      : { mode: "protect", mission: null };
  }

  if (!optionalNextSuppressed.value && safeOptionalMissions.value.length) {
    return buildDailyMomentumAction("optional", safeOptionalMissions.value[0]);
  }

  return { mode: "complete", mission: null };
});

const dailyMomentumActions = computed(() => {
  const nextAction = dailyMomentumNextAction.value;

  if (!dailyMomentumTodaySafe.value) {
    return [{
      key: "protect",
      icon: "protect-today",
      variant: "primary",
      label: t("missions.dailyMomentum.actions.protect"),
      mission: nextAction.mission,
    }];
  }

  if (optionalExplorerExpanded.value || selectedOptionalExplorerMission.value) {
    return [{
      key: "finish",
      icon: "finish-today",
      variant: "primary",
      label: t("missions.dailyMomentum.actions.finish"),
    }, {
      key: "hide_choices",
      icon: "hide-choices",
      variant: "secondary",
      label: t("missions.dailyMomentum.actions.hideChoices"),
    }];
  }

  if (nextAction.mode === "optional" && nextAction.mission && !dailyMomentumAllPathsComplete.value) {
    const actions = [{
      key: "view_choices",
      icon: "view-choices",
      variant: "primary",
      label: t("missions.dailyMomentum.actions.viewChoices"),
      mission: nextAction.mission,
    }, {
      key: "finish",
      icon: "finish-today",
      variant: "secondary",
      label: t("missions.dailyMomentum.actions.finish"),
    }];

    return actions;
  }

  const actions = [{
    key: "finish",
    icon: "finish-today",
    variant: "primary",
    label: t("missions.dailyMomentum.actions.finish"),
  }];

  if (optionalExplorerMissions.value.length && !optionalNextSuppressed.value) {
    actions.push({
      key: "view_choices",
      icon: "view-choices",
      variant: "secondary",
      label: t("missions.dailyMomentum.actions.viewChoices"),
    });
  }

  return actions;
});

const showDailyMomentumBar = computed(() => {
  return Boolean(!loading.value && !error.value && localizedMissions.value.length);
});

watch(showDailyMomentumExplorePaths, (canExplore) => {
  if (!canExplore) {
    explorePathsPanelOpen.value = false;
  }
});

const showTodaySavedBody = computed(() => {
  if (optionalNextMission.value) return true;
  if (finishedForTodayNarrative.value) return false;
  if (agendaNarrative.value?.mood === "sleeping") return false;

  return guidanceAgenda.value?.next_action_type !== "done_for_today";
});

const missionReminderCount = computed(() => {
  return localizedMissions.value.filter((mission) => missionHasStatus(mission, "remind_later")).length;
});

const missionFocusState = computed(() => {
  if (loading.value) {
    return {
      active: true,
      reason: "loading",
      todaySafe: false,
      hasActionableSuggestion: false,
      reminderCount: 0,
    };
  }

  if (restModeActive.value) {
    return {
      active: true,
      reason: "rest_mode",
      todaySafe: isTodaySaved.value,
      hasActionableSuggestion: false,
      reminderCount: missionReminderCount.value,
    };
  }

  const agendaType = guidanceAgenda.value?.next_action_type || "";
  const hasDueReminder = Boolean(dueReminderMission.value);
  const hasPendingPrimary = pendingMissions.value.some((mission) => {
    return normalizedMissionIntensity(mission) !== "bonus";
  });
  const hasActiveTinyFlow = Boolean(
    focusMission.value &&
    normalizedMissionIntensity(focusMission.value) === "tiny" &&
    !missionHasStatus(focusMission.value, "done", "skipped"),
  );
  const hasOptionalBonusFocus = Boolean(optionalNextMission.value);
  const isCompletionUnacknowledged = Boolean(isTodaySaved.value && !optionalNextSuppressed.value);
  const isFutureReminderOnly = Boolean(
    !hasPendingPrimary &&
    !hasDueReminder &&
    deferredMissions.value.length &&
    deferredMissions.value.every((mission) => !isReminderDue(mission)),
  );

  let reason = "";
  if (props.firstRunFocus) reason = "first_run";
  else if (hasDueReminder) reason = "due_reminder";
  else if (hasActiveTinyFlow) reason = "tiny_flow";
  else if (hasOptionalBonusFocus) reason = "optional_bonus";
  else if (hasPendingPrimary || agendaType === "primary_mission") reason = "primary_mission";
  else if (isCompletionUnacknowledged) reason = "completion_unacknowledged";
  else if (isFutureReminderOnly) reason = "future_reminder_only";
  else reason = "done_for_today";

  const active = !["future_reminder_only", "done_for_today"].includes(reason);

  return {
    active,
    reason,
    todaySafe: isTodaySaved.value,
    reminderCount: missionReminderCount.value,
    hasActionableSuggestion: Boolean(
      hasDueReminder ||
      hasPendingPrimary ||
      hasActiveTinyFlow ||
      hasOptionalBonusFocus ||
      guidanceActions.value.length,
    ),
  };
});

const guidanceActions = computed(() => {
  const actions = Array.isArray(ringoGuidance.value?.actions)
    ? ringoGuidance.value.actions
    : [];

  if (!actions.length || !focusMission.value || missionGuide.value?.complete || isTodaySaved.value) {
    return [];
  }

  const seen = new Set();

  return actions.filter((action) => {
    const type = action?.type;
    if (!SUPPORTED_GUIDANCE_ACTIONS.has(type) || seen.has(type)) return false;
    seen.add(type);
    return true;
  });
});

const anyMissionActionPanelOpen = computed(() => {
  return !!(reminderPanelMissionId.value || skipReasonPanelMissionId.value);
});

const showFocusMissionActions = computed(() => {
  return !!(
    focusMission.value
    && showFocusMissionCard.value
    && !anyMissionActionPanelOpen.value
    && !missionHasStatus(focusMission.value, "done")
  );
});

const showMissionNotice = computed(() => {
  if (!notice.value) return false;

  return noticeType.value !== "success" && !rewardSequenceSteps.value.length;
});

const coachActionPanel = computed(() => {
  return !!(
    showCoach.value
    || guidanceMission.value
    || guidanceActions.value.length
    || finishedForTodayNarrative.value
    || dailySummaryNarrative.value
    || agendaNarrative.value
    || todaySavedLabel.value
    || interactionNarrative.value
    || completionNarrative.value
  );
});

const reminderOptions = computed(() => {
  return REMINDER_OPTION_KEYS.map((key) => ({
    key,
    label: t(`missions.remindOptions.${key}`),
  }));
});

const skipReasonOptions = computed(() => {
  return SKIP_REASON_OPTIONS.map((option) => ({
    ...option,
    label: t(`missions.skipReasons.${option.key}`),
  }));
});

const showFirstRunActionEducation = computed(() => {
  return Boolean(
    props.firstRunFocus &&
    focusMission.value &&
    !missionGuide.value?.complete
  );
});

const showFirstRunMissionIntro = computed(() => {
  return Boolean(
    props.firstRunFocus &&
    focusMission.value &&
    !missionGuide.value?.complete
  );
});

const showMissionStatusToggle = computed(() => {
  return false;
});

const showSecondaryMissionStatus = computed(() => {
  return Boolean(
    showOtherMissionList.value &&
    !props.focusModeActive &&
    !props.firstRunFocus
  );
});

const restModeSprite = computed(() => resolveRingoSprite("sleeping"));

const nearestFutureReminder = computed(() => {
  return sortReminderMissions(
    deferredMissions.value.filter((mission) => !isReminderDue(mission)),
  )[0] || null;
});

const nearestFutureReminderLabel = computed(() => {
  const timestamp = reminderTimestamp(nearestFutureReminder.value);
  if (!Number.isFinite(timestamp)) return "";

  const minutes = Math.max(1, Math.round((timestamp - Date.now()) / 60000));
  if (minutes < 60) {
    return t("missions.restMode.minutes", { count: minutes });
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (!remainingMinutes) {
    return t("missions.restMode.hours", { count: hours });
  }

  return t("missions.restMode.hoursMinutes", {
    hours,
    minutes: remainingMinutes,
  });
});

function clearNarrativeState() {
  interactionNarrative.value = null;
  completionNarrative.value = null;
}

function setNarrative(narrative) {
  const payload = {
    message: narrative?.message || "",
    mood: narrative?.mood || "idle",
  };

  if (narrative?.type === "completion") {
    completionNarrative.value = payload;
    interactionNarrative.value = null;
    return;
  }

  interactionNarrative.value = payload;
}

function setInteractionNarrative(messageKey, mood, params = {}) {
  setNarrative({
    message: t(messageKey, params),
    mood,
    type: "interaction",
  });
}

async function scrollTelegramPromptIntoView() {
  await nextTick();

  const target = telegramPromptRef.value?.$el || telegramPromptRef.value;

  if (target?.scrollIntoView) {
    target.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  }
}

function refreshTelegramSettingsFromPayload(settings) {
  if (!settings) return;

  telegramSettings.value = {
    ...telegramSettings.value,
    ...settings,
  };
}

function dismissTelegramReminderPrompt() {
  telegramReminderPrompt.value = null;
  telegramPromptError.value = "";
}

function showTelegramPromptAfterReminder() {
  telegramPromptError.value = "";

  if (!telegramConnected.value) {
    telegramReminderPrompt.value = {
      mode: "connect",
    };
    scrollTelegramPromptIntoView();
    return;
  }

  if (!telegramRemindersEnabled.value) {
    telegramReminderPrompt.value = {
      mode: "disabled",
    };
    scrollTelegramPromptIntoView();
    return;
  }

  telegramReminderPrompt.value = null;
}

async function connectTelegramFromReminder() {
  telegramPromptBusy.value = true;
  telegramPromptError.value = "";

  try {
    const { data } = await api.post("/api/me/telegram/connect-code", {});
    telegramConnectCode.value = data?.connect_code || null;
    const link = telegramConnectLink.value;
    if (link) {
      window.open(link, "_blank", "noopener,noreferrer");
    }
  } catch (err) {
    telegramPromptError.value = err?.response?.data?.error || t("missions.telegramPrompt.connectError");
  } finally {
    telegramPromptBusy.value = false;
  }
}

async function enableTelegramRemindersFromPrompt() {
  telegramPromptBusy.value = true;
  telegramPromptError.value = "";

  try {
    const { data } = await api.patch("/api/me/telegram/settings", {
      reminders_enabled: true,
    });
    refreshTelegramSettingsFromPayload(data?.settings);
    telegramReminderPrompt.value = null;
  } catch (err) {
    telegramPromptError.value = err?.response?.data?.error || t("missions.telegramPrompt.enableError");
  } finally {
    telegramPromptBusy.value = false;
  }
}

async function loadMissions() {
  loading.value = true;
  error.value = "";
  clearNarrativeState();
  manualFocusMissionId.value = null;
  restModeActive.value = false;
  optionalExplorerExpanded.value = false;
  selectedOptionalExplorerMissionId.value = null;
  selectedMomentumPathId.value = "";
  explorePathsPanelOpen.value = false;
  showOtherMissions.value = true;
  optionalSuggestionRequested.value = false;
  selectedTimelineMissionId.value = null;
  reminderPanelMissionId.value = null;
  customReminderPanelMissionId.value = null;
  customReminderTime.value = "";
  skipReasonPanelMissionId.value = null;

  try {
    const [missionsResult, guidanceResult, telegramResult, pathsResult] = await Promise.allSettled([
      api.get("/me/today-missions"),
      api.get("/me/ringo/today"),
      api.get("/api/me/telegram/settings"),
      api.get("/paths"),
    ]);

    if (missionsResult.status === "rejected") {
      throw missionsResult.reason;
    }

    const { data } = missionsResult.value;
    ringoGuidance.value = guidanceResult.status === "fulfilled"
      ? guidanceResult.value?.data || null
      : null;
    if (telegramResult.status === "fulfilled") {
      telegramSettings.value = {
        ...telegramSettings.value,
        ...(telegramResult.value?.data?.settings || {}),
      };
    }
    pathCatalog.value = pathsResult.status === "fulfilled"
      ? pathsResult.value?.data?.items || []
      : [];
    date.value = data?.date || "";
    ringo.value = data?.ringo || null;
    if (ringo.value?.state !== dismissedCoachState.value) {
      dismissedCoachState.value = "";
    }
    missions.value = data?.missions || [];
    emit("loaded", {
      error: "",
      ringo: localizedRingo.value,
      missions: localizedMissions.value,
      state: ringo.value?.state || "",
    });
  } catch (e) {
    ringoGuidance.value = null;
    pathCatalog.value = [];
    error.value = e?.response?.data?.error || e?.message || String(e);
    emit("loaded", {
      error: error.value,
      ringo: null,
      missions: [],
      state: "error",
    });
  } finally {
    loading.value = false;
  }
}

function completeFirstRunFocus() {
  if (props.firstRunFocus) {
    emit("first-run-complete");
  }
}

async function runMissionAction(mission, action, request, options = {}) {
  busyId.value = mission.mission_id;
  busyAction.value = action;
  error.value = "";

  const shouldBuildReward = action === "done";
  const rewardBeforeSnapshot = shouldBuildReward
    ? buildCurrentRewardSnapshot(mission)
    : null;

  try {
    const { data } = await request();

    notice.value = options.successNotice || (action === "done"
      ? data?.checkin?.already_checked
        ? t("missions.alreadySecuredNotice")
        : t("missions.securedNotice")
      : action === "remind"
        ? t("missions.reminderNotice")
        : t("missions.skipNotice"));

    noticeType.value = action === "done"
      ? "success"
      : action === "remind"
        ? "reminder"
        : "muted";

    const completedMission = {
      ...(mission || {}),
      ...(data?.mission || {}),
      title: mission.title,
      description: mission.description,
      key: data?.mission?.key || data?.mission?.mission_key || mission.key || mission.mission_key || "",
      challenge_name: data?.mission?.challenge_name || mission.challenge_name,
      path_title: data?.mission?.path_title || mission.path_title,
    };

    applyMissionResponse(data, mission);
    completeFirstRunFocus();

    await loadMissions();

    if (shouldBuildReward) {
      const rewardAfterSnapshot = buildCurrentRewardSnapshot(completedMission, data);
      const rewardDelta = buildRewardDelta(rewardBeforeSnapshot, rewardAfterSnapshot, data);
      const rewardResult = buildMissionCompletionRewardSteps(rewardDelta, data, { t });

      rewardSequenceSteps.value = rewardResult.steps;
      rewardSequenceSprite.value = missionRewardIntensity(data, mission) === "bonus"
        ? "happy"
        : "celebration";

      if (import.meta.env.DEV) {
        console.debug("[reward-sequence]", {
          alreadyDone: rewardResult.normalized.alreadyDone,
          xpAwarded: rewardResult.normalized.xpAwarded,
          backendSteps: rewardResult.backendSteps.length,
          frontendSteps: rewardResult.frontendSteps.length,
          finalSteps: rewardResult.steps.length,
        });
      }
    }

    if (data?.checkin?.ok) {
      emit("checked-in", {
        ...data,
        source: "mission_completion",
        mission: completedMission,
      });
    }

    if (action === "remind") {
      preferMainMissionAfterReminder(mission);
      selectedTimelineMissionId.value = mission.mission_id;
      showTelegramPromptAfterReminder();
    }

    if (options.narrative) {
      setNarrative(options.narrative);
    } else if (action === "done") {
      completionNarrative.value = missionCompletionNarrative(data, mission);
    }
  } catch (e) {
    const errorCode = e?.response?.data?.error || e?.message || String(e);

    if (action === "remind" && errorCode === "reminder_after_next_reset") {
      error.value = "";
      notice.value = t("missions.remindOptions.afterResetBlockedNotice");
      noticeType.value = "reminder";
      setInteractionNarrative("missions.narrative.remindBlockedAfterReset", "thinking");
    } else {
      error.value = errorCode;
    }
  } finally {
    busyId.value = null;
    busyAction.value = "";
    busyReminderOption.value = "";
    busySkipReason.value = "";
  }
}


function markDone(mission) {
  return runMissionAction(
    mission,
    "done",
    () => api.post(`/me/missions/${mission.mission_id}/done`, {}),
  );
}

function remindLater(mission) {
  if (!mission || missionHasStatus(mission, "done")) return null;

  notice.value = "";
  reminderPanelMissionId.value = mission.mission_id;
  customReminderPanelMissionId.value = null;
  customReminderTime.value = "";
  skipReasonPanelMissionId.value = null;
  setInteractionNarrative("missions.narrative.remindOpen", "thinking");
  return focusMissionCard(mission);
}

function fallbackReminderAt() {
  return new Date(Date.now() + 2 * 60 * 60 * 1000);
}

function nextLocalReminderSlot(hour, minute = 0) {
  const now = new Date();
  const target = new Date(now);
  target.setHours(hour, minute, 0, 0);

  if (target <= now) {
    target.setDate(target.getDate() + 1);
  }

  return target;
}

function reminderAtForOption(key) {
  const now = new Date();

  if (key === "fifteenMinutes") {
    return new Date(now.getTime() + 15 * 60 * 1000);
  }

  if (key === "oneHour") {
    return new Date(now.getTime() + 60 * 60 * 1000);
  }

  if (key === "evening") {
    return nextLocalReminderSlot(18, 0);
  }

  if (key === "tonight") {
    return nextLocalReminderSlot(22, 0);
  }

  return fallbackReminderAt();
}

function isReminderPanelOpen(mission) {
  return !!(
    mission?.mission_id
    && sameMissionId(reminderPanelMissionId.value, mission.mission_id)
    && !missionHasStatus(mission, "done")
  );
}

function isCustomReminderPanelOpen(mission) {
  return !!(
    mission?.mission_id
    && sameMissionId(customReminderPanelMissionId.value, mission.mission_id)
    && isReminderPanelOpen(mission)
  );
}

function isReminderOptionLoading(mission, key) {
  return !!(
    mission?.mission_id
    && busyId.value === mission.mission_id
    && busyAction.value === "remind"
    && busyReminderOption.value === key
  );
}

function blockReminderAfterReset() {
  busyReminderOption.value = "";
  notice.value = t("missions.remindOptions.afterResetBlockedNotice");
  noticeType.value = "reminder";
  setInteractionNarrative("missions.narrative.remindBlockedAfterReset", "thinking");
}

function blockPastCustomReminder() {
  busyReminderOption.value = "";
  notice.value = t("missions.remindOptions.pastTimeNotice");
  noticeType.value = "reminder";
  setInteractionNarrative("missions.narrative.remindBlockedPastTime", "thinking");
}

async function planTodayReminders() {
  if (planningReminders.value) return;

  planningReminders.value = true;
  error.value = "";
  notice.value = "";
  try {
    const { data } = await api.post("/me/missions/plan-reminders", {});
    await loadMissions();
    showOtherMissions.value = true;
    const scheduledCount = Number(data?.summary?.scheduled_count || 0);
    const unscheduledCount = Number(data?.summary?.unscheduled_count || 0);
    const firstScheduledMissionId = data?.scheduled?.[0]?.mission_id;

    if (firstScheduledMissionId) {
      selectedTimelineMissionId.value = firstScheduledMissionId;
      manualFocusMissionId.value = firstScheduledMissionId;
    }

    notice.value = scheduledCount
      ? t("missions.planRemindersNotice", { count: scheduledCount, unscheduled: unscheduledCount })
      : t("missions.planRemindersNoneNotice");
    noticeType.value = scheduledCount ? "reminder" : "muted";
    setNarrative({
      message: scheduledCount
        ? t("missions.narrative.planRemindersDone", { count: scheduledCount, unscheduled: unscheduledCount })
        : t("missions.narrative.planRemindersNone"),
      mood: scheduledCount ? "encouraging" : "thinking",
      type: "interaction",
    });
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    planningReminders.value = false;
  }
}

async function planMissionReminder(mission) {
  if (!mission?.mission_id || missionHasStatus(mission, "done", "skipped")) return null;

  busyId.value = mission.mission_id;
  busyAction.value = "remind";
  busyReminderOption.value = "ringo";
  error.value = "";
  notice.value = "";
  try {
    const { data } = await api.post(`/me/missions/${mission.mission_id}/plan-reminder`, {});
    const reminderTime = formattedReminderTime(data?.scheduled?.reminder_at || data?.mission?.reminder_at);
    applyMissionResponse(data, mission);
    await loadMissions();
    selectedTimelineMissionId.value = mission.mission_id;
    showOtherMissions.value = true;
    showTelegramPromptAfterReminder();
    notice.value = t("missions.remindOptions.ringoConfirmation", { time: reminderTime });
    noticeType.value = "reminder";
    setNarrative({
      message: t("missions.narrative.ringoReminderSet", { time: reminderTime }),
      mood: "happy",
      type: "interaction",
    });
  } catch (e) {
    const errorCode = e?.response?.data?.error || e?.message || String(e);
    if (errorCode === "no_safe_reminder_time") {
      notice.value = t("missions.remindOptions.noSafeRingoTime");
      noticeType.value = "reminder";
      setInteractionNarrative("missions.narrative.noSafeRingoReminder", "thinking");
    } else {
      error.value = errorCode;
    }
  } finally {
    busyId.value = null;
    busyAction.value = "";
    busyReminderOption.value = "";
  }
}

function selectReminderOption(mission, option) {
  if (!mission) return null;

  busyReminderOption.value = option?.key || "";
  const reminderAtDate = reminderAtForOption(option?.key);
  const tomorrowSlot = reminderTomorrowSlotKey(reminderAtDate);
  const afterNextReset = isAfterNextRingoReset(reminderAtDate);
  const reminderAt = reminderAtDate.toISOString();
  const timeLabel = formattedReminderTime(reminderAtDate);
  if (afterNextReset) {
    blockReminderAfterReset();
    return null;
  }

  const confirmationKey = afterNextReset
    ? "missions.remindOptions.confirmationAfterReset"
    : option?.key === "evening" && tomorrowSlot === "evening"
      ? "missions.remindOptions.confirmationTomorrowEvening"
      : option?.key === "tonight" && tomorrowSlot === "night"
        ? "missions.remindOptions.confirmationTomorrowNight"
        : "missions.remindOptions.confirmation";
  const narrativeKey = afterNextReset
    ? "missions.narrative.remindConfirmedAfterReset"
    : option?.key === "evening" && tomorrowSlot === "evening"
      ? "missions.narrative.remindConfirmedTomorrowEvening"
      : option?.key === "tonight" && tomorrowSlot === "night"
        ? "missions.narrative.remindConfirmedTomorrowNight"
        : "missions.narrative.remindConfirmed";
  const successNotice = option?.label
    ? t(confirmationKey, { time: option.label, exactTime: timeLabel })
    : t("missions.remindOptions.fallbackConfirmation");

  return runMissionAction(
    mission,
    "remind",
    () => api.post(`/me/missions/${mission.mission_id}/remind-later`, {
      reminder_at: reminderAt,
    }),
    {
      successNotice,
      narrative: {
        message: option?.label
          ? t(narrativeKey, { time: option.label, exactTime: timeLabel })
          : t("missions.narrative.remindConfirmedFallback"),
        mood: "happy",
        type: "interaction",
      },
    },
  );
}

function openCustomReminderTime(mission) {
  if (!mission) return null;

  customReminderPanelMissionId.value = mission.mission_id;
  customReminderTime.value = "";
  notice.value = "";
  setInteractionNarrative("missions.narrative.remindCustomOpen", "thinking");
  return focusMissionCard(mission);
}

function customReminderAt(value) {
  const match = /^(\d{2}):(\d{2})$/.exec(String(value || ""));
  if (!match) return { error: "missing" };

  const hour = Number(match[1]);
  const minute = Number(match[2]);
  if (hour > 23 || minute > 59) return { error: "missing" };

  const now = new Date();
  const candidate = new Date(now);
  candidate.setHours(hour, minute, 0, 0);

  if (candidate > now) return { date: candidate };

  const nextReset = parsedNextResetAt();
  if (nextReset) {
    const tomorrowCandidate = new Date(candidate);
    tomorrowCandidate.setDate(tomorrowCandidate.getDate() + 1);

    if (tomorrowCandidate > now && tomorrowCandidate < nextReset) {
      return { date: tomorrowCandidate };
    }
  }

  return { error: "past" };
}

function selectCustomReminderTime(mission) {
  if (!mission) return null;

  busyReminderOption.value = "custom";
  const resolved = customReminderAt(customReminderTime.value);

  if (resolved.error === "missing") {
    busyReminderOption.value = "";
    notice.value = t("missions.remindOptions.customHelp");
    noticeType.value = "reminder";
    setInteractionNarrative("missions.narrative.remindCustomOpen", "thinking");
    return null;
  }

  if (resolved.error === "past") {
    blockPastCustomReminder();
    return null;
  }

  const reminderAtDate = resolved.date;
  if (isAfterNextRingoReset(reminderAtDate)) {
    blockReminderAfterReset();
    return null;
  }

  const reminderAt = reminderAtDate.toISOString();
  const timeLabel = formattedReminderTime(reminderAtDate);

  return runMissionAction(
    mission,
    "remind",
    () => api.post(`/me/missions/${mission.mission_id}/remind-later`, {
      reminder_at: reminderAt,
    }),
    {
      successNotice: t("missions.remindOptions.confirmation", { time: timeLabel, exactTime: timeLabel }),
      narrative: {
        message: t("missions.narrative.remindConfirmed", { time: timeLabel, exactTime: timeLabel }),
        mood: "happy",
        type: "interaction",
      },
    },
  );
}

function closeReminderPanel() {
  reminderPanelMissionId.value = null;
  customReminderPanelMissionId.value = null;
  customReminderTime.value = "";
  clearNarrativeState();
}

function skipMission(mission) {
  if (!mission || missionHasStatus(mission, "done", "skipped")) return null;

  notice.value = "";
  skipReasonPanelMissionId.value = mission.mission_id;
  reminderPanelMissionId.value = null;
  customReminderPanelMissionId.value = null;
  customReminderTime.value = "";
  setInteractionNarrative("missions.narrative.skipOpen", "concerned");
  return focusMissionCard(mission);
}

function isSkipReasonPanelOpen(mission) {
  return !!(
    mission?.mission_id
    && sameMissionId(skipReasonPanelMissionId.value, mission.mission_id)
    && !missionHasStatus(mission, "done", "skipped")
  );
}

function isSkipReasonLoading(mission, key) {
  return !!(
    mission?.mission_id
    && busyId.value === mission.mission_id
    && busyAction.value === "skip"
    && busySkipReason.value === key
  );
}

function closeSkipReasonPanel() {
  skipReasonPanelMissionId.value = null;
  clearNarrativeState();
}

function selectSkipReason(mission, reason) {
  if (!mission) return null;

  busySkipReason.value = reason?.key || "";
  const isOptionalSkip = isTodaySaved.value || normalizedMissionIntensity(mission) === "bonus";
  const hasSkipReason = reason?.key && reason.key !== "withoutReason";
  const successNotice = isOptionalSkip
    ? t("missions.optionalSkipNotice")
    : hasSkipReason
      ? t("missions.skipReasons.confirmationWithReason", { reason: reason.label })
      : t("missions.skipReasons.confirmationWithoutReason");
  const narrativeMessage = isOptionalSkip
    ? t("missions.narrative.skipOptionalConfirmed")
    : hasSkipReason
      ? t("missions.narrative.skipConfirmedWithReason", { reason: reason.label })
      : t("missions.narrative.skipConfirmedWithoutReason");
  const requestBody = reason?.reason ? { reason: reason.reason } : {};

  return runMissionAction(
    mission,
    "skip",
    () => postMissionSkip(mission.mission_id, requestBody),
    {
      successNotice,
      narrative: {
        message: narrativeMessage,
        mood: isOptionalSkip ? "calm" : "concerned",
        type: "interaction",
      },
    },
  );
}

async function postMissionSkip(missionId, body) {
  const hasReason = !!body?.reason;

  try {
    return await api.post(`/me/missions/${missionId}/skip`, body || {});
  } catch (e) {
    const error = e?.response?.data?.error;
    const canRetryWithoutReason = hasReason && [
      "invalid_skip_reason",
      "skip_reason_too_long",
      "unsupported_skip_reason",
    ].includes(error);

    if (!canRetryWithoutReason) {
      throw e;
    }

    return api.post(`/me/missions/${missionId}/skip`, {});
  }
}

function applyMissionResponse(data, fallbackMission) {
  const responseMission = data?.mission;
  const missionId = responseMission?.mission_id || fallbackMission?.mission_id;
  if (!missionId) return;

  missions.value = missions.value.map((mission) => {
    if (!sameMissionId(mission.mission_id, missionId)) return mission;

    return {
      ...mission,
      ...(responseMission || {}),
      title: mission.title,
      description: mission.description,
      challenge_name: mission.challenge_name,
      path_title: mission.path_title,
    };
  });
}

function missionRewardXpAwarded(data) {
  const amount = Number(data?.mission?.xp_awarded);
  return Number.isFinite(amount) && amount > 0 ? amount : 0;
}

function missionRewardAlreadyDone(data) {
  return Boolean(data?.mission?.already_done);
}

function missionRewardIntensity(data, mission) {
  return normalizedMissionIntensity({
    ...(mission || {}),
    ...(data?.mission || {}),
  });
}

function buildCurrentRewardSnapshot(mission, completionResult = null) {
  return buildRewardSnapshot({
    missions: localizedMissions.value,
    pathGroups: dailyMomentumPathGroups.value,
    stats: props.stats,
    guidanceProgress: ringoGuidance.value?.progress || null,
    mission,
    completionResult,
    fallbacks: {
      path: t("missions.fallbackPath"),
      challenge: t("missions.fallbackChallenge"),
    },
  });
}

function missionCompletionNarrative(data, mission) {
  if (missionRewardAlreadyDone(data)) {
    return {
      message: t("missions.narrative.alreadyCompleted", { mission: mission.title }),
      mood: "calm",
    };
  }

  const xpAwarded = missionRewardXpAwarded(data);
  if (xpAwarded <= 0) {
    return {
      message: t("missions.narrative.completedNoXp", { mission: mission.title }),
      mood: "proud",
    };
  }

  return {
    message: t("missions.narrative.completed", { mission: mission.title }),
    mood: missionRewardIntensity(data, mission) === "bonus" ? "happy" : "proud",
  };
}

function finishRewardSequence() {
  rewardSequenceSteps.value = [];
  showOtherMissions.value = true;
}

function handleRewardSequenceAction(action) {
  if (action?.key === "finish_today") {
    finishForToday();
    return;
  }

  if (action?.key === "view_choices") {
    selectedMomentumPathId.value = "";
    viewRemainingMissions();
  }
}

function missionActionIcon(key) {
  return resolveActionIcon(key);
}

function normalizedPathId(value) {
  const id = String(value ?? "").trim();
  return id && id !== "null" && id !== "undefined" ? id : "";
}

function pathChallengePreview(path) {
  const raw = Array.isArray(path?.challengePreview)
    ? path.challengePreview
    : Array.isArray(path?.preview_challenges)
      ? path.preview_challenges
      : Array.isArray(path?.challenges)
        ? path.challenges
        : [];

  return raw
    .map((challenge) => {
      if (typeof challenge === "string") return localizeChallenge({ name: challenge }, locale.value).name || challenge;
      const localizedChallenge = localizeChallenge(challenge, locale.value) || challenge;
      return localizedChallenge.name || localizedChallenge.title || "";
    })
    .filter(Boolean)
    .slice(0, 2);
}

function pathChallengeCount(path, preview = []) {
  const candidates = [
    path?.available_challenge_count,
    path?.available_challenges_count,
    path?.challenge_count,
    path?.challenges_count,
    Array.isArray(path?.challenges) ? path.challenges.length : null,
    preview.length,
  ];

  const count = candidates.map((value) => Number(value)).find((value) => Number.isFinite(value) && value > 0);
  return count || 0;
}

function buildDailyMomentumAction(mode, mission) {
  return {
    mode,
    mission,
    title: mission?.title || t(`missions.dailyMomentum.next.${mode}.title`),
    meta: dailyMomentumMissionMeta(mission),
  };
}

function dailyMomentumMissionMeta(mission) {
  if (!mission) return "";

  const type = missionTypeLabel(mission);
  const minutes = missionEstimatedMinutes(mission);
  if (minutes) {
    return t("missions.dailyMomentum.next.missionMetaWithTime", { type, minutes });
  }

  return t("missions.dailyMomentum.next.missionMeta", { type });
}

function selectDailyMomentumPath(path) {
  if (!path?.key) return;

  explorePathsPanelOpen.value = false;
  selectedMomentumPathId.value = path.key;
  closeReminderPanel();
  closeSkipReasonPanel();

  if (optionalExplorerMissions.value.length) {
    optionalExplorerExpanded.value = true;
    selectedOptionalExplorerMissionId.value = null;
    optionalSuggestionRequested.value = false;
    showOtherMissions.value = false;
    setInteractionNarrative("missions.dailyMomentum.narrative.pathSelected", "thinking", {
      path: path.title || t("missions.fallbackPath"),
    });
    return;
  }

  const mission = path.missions?.find((item) => {
    return normalizedMissionIntensity(item) !== "bonus" && missionHasStatus(item, "pending", "remind_later");
  }) || path.missions?.[0];

  if (mission?.mission_id) {
    manualFocusMissionId.value = mission.mission_id;
    setInteractionNarrative("missions.dailyMomentum.narrative.pathMissionFocused", "focus", {
      path: path.title || t("missions.fallbackPath"),
    });
    focusMissionCard(mission);
  }
}

function selectDailyMomentumNextAction(action) {
  const mission = action?.mission;
  if (!mission?.mission_id) return;

  closeReminderPanel();
  closeSkipReasonPanel();

  if (dailyMomentumTodaySafe.value && action.mode === "optional") {
    optionalExplorerExpanded.value = false;
    selectedOptionalExplorerMissionId.value = mission.mission_id;
    optionalSuggestionRequested.value = false;
    setInteractionNarrative(selectedOptionalExplorerNarrativeKey(mission), selectedOptionalExplorerNarrativeMood(mission), {
      mission: mission.title || t("missions.fallbackMission"),
    });
    nextTick(() => {
      document
        .getElementById("optional-explorer-selected")
        ?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
    return;
  }

  manualFocusMissionId.value = mission.mission_id;
  optionalExplorerExpanded.value = false;
  selectedOptionalExplorerMissionId.value = null;
  setInteractionNarrative("missions.dailyMomentum.narrative.nextActionFocused", "focus", {
    mission: mission.title || t("missions.fallbackMission"),
  });
  focusMissionCard(mission);
}

function handleDailyMomentumAction(action) {
  if (!action?.key) return;

  explorePathsPanelOpen.value = false;

  if (action.key === "finish") {
    finishForToday();
    return;
  }

  if (action.key === "view_choices") {
    selectedMomentumPathId.value = "";
    viewRemainingMissions();
    return;
  }

  if (action.key === "hide_choices") {
    hideOptionalMissionExplorer();
    showOptionalExplorerRoot();
    return;
  }

  if (action.key === "protect") {
    selectDailyMomentumNextAction({
      mode: "protect",
      mission: action.mission || dailyMomentumNextAction.value?.mission,
    });
  }
}

function exploreDailyMomentumPaths() {
  if (!showDailyMomentumExplorePaths.value) return;

  explorePathsPanelOpen.value = true;
  setInteractionNarrative("missions.dailyMomentum.narrative.explorePaths", "thinking");
}

function closeExplorePathsPanel() {
  explorePathsPanelOpen.value = false;
}

function openPathsFromExplorePanel() {
  explorePathsPanelOpen.value = false;
  router.push({ path: "/paths", query: { source: "momentum" } }).catch(() => { });
}

function explainDailyMomentumStrike() {
  setInteractionNarrative(
    dailyMomentumTodaySafe.value
      ? "missions.dailyMomentum.narrative.strikeSafe"
      : "missions.dailyMomentum.narrative.strikeNotSafe",
    dailyMomentumTodaySafe.value ? "happy" : "focus",
  );
}

function finishForToday() {
  optionalNextSuppressed.value = true;
  optionalSuggestionRequested.value = false;
  manualFocusMissionId.value = null;
  restModeActive.value = true;
  optionalExplorerExpanded.value = false;
  selectedOptionalExplorerMissionId.value = null;
  selectedMomentumPathId.value = "";
  missionStatusExpanded.value = false;
  showOtherMissions.value = true;
  setInteractionNarrative("missions.finishedForTodayMessage", "sleeping");
}

function suggestOptionalStep() {
  optionalSuggestionRequested.value = true;
  optionalExplorerExpanded.value = false;
  missionStatusExpanded.value = false;
  showOtherMissions.value = false;
  setInteractionNarrative("missions.narrative.optionalSuggestionRequested", "happy");
}

function viewRemainingMissions() {
  optionalExplorerExpanded.value = true;
  missionStatusExpanded.value = false;
  showOtherMissions.value = false;
  selectedOptionalExplorerMissionId.value = null;
  setInteractionNarrative("missions.narrative.viewRemainingOptional", "thinking");
}

function hideOptionalMissionExplorer() {
  optionalExplorerExpanded.value = false;
  selectedOptionalExplorerMissionId.value = null;
  selectedMomentumPathId.value = "";
}

function selectOptionalExplorerPath(path) {
  selectedOptionalExplorerMissionId.value = null;
  closeReminderPanel();
  closeSkipReasonPanel();
  const stats = path?.stats || {};
  setInteractionNarrative(optionalPathNarrativeKey(stats), "thinking", {
    path: path?.title || t("missions.fallbackPath"),
    count: optionalGroupNarrativeCount(stats),
  });
}

function selectOptionalExplorerChallenge(challenge) {
  selectedOptionalExplorerMissionId.value = null;
  closeReminderPanel();
  closeSkipReasonPanel();
  const stats = challenge?.stats || {};
  setInteractionNarrative(optionalChallengeNarrativeKey(stats), "thinking", {
    challenge: challenge?.title || t("missions.fallbackChallenge"),
    count: optionalGroupNarrativeCount(stats),
  });
}

function showOptionalExplorerRoot() {
  selectedOptionalExplorerMissionId.value = null;
  closeReminderPanel();
  closeSkipReasonPanel();
  setInteractionNarrative("missions.narrative.backToOptionalChoices", "thinking");
}

function selectOptionalExplorerMission(mission) {
  if (!mission?.mission_id) return;

  selectedOptionalExplorerMissionId.value = mission.mission_id;
  optionalExplorerExpanded.value = false;
  closeReminderPanel();
  closeSkipReasonPanel();
  setInteractionNarrative(selectedOptionalExplorerNarrativeKey(mission), selectedOptionalExplorerNarrativeMood(mission), {
    mission: mission.title || t("missions.fallbackMission"),
  });
}

function backToOptionalChoices() {
  selectedOptionalExplorerMissionId.value = null;
  optionalExplorerExpanded.value = true;
  closeReminderPanel();
  closeSkipReasonPanel();
  setInteractionNarrative("missions.narrative.backToOptionalChoices", "thinking");
}

function restForNow() {
  missionStatusExpanded.value = false;
}

function showDashboardFromRest() {
  restModeActive.value = false;
  emit("show-dashboard");
}

function hideMissionStatusDetails() {
  if (props.focusModeActive) {
    missionStatusExpanded.value = false;
    return;
  }

  showOtherMissions.value = false;
}

function focusOptionalNextMission(mission) {
  if (!mission) return null;

  manualFocusMissionId.value = mission.mission_id;
  showOtherMissions.value = true;
  return focusMissionCard(mission);
}

function remindOptionalNextMission(mission) {
  if (!mission) return null;

  manualFocusMissionId.value = mission.mission_id;
  showOtherMissions.value = true;
  return remindLater(mission);
}

function skipOptionalNextMission(mission) {
  if (!mission) return null;

  manualFocusMissionId.value = mission.mission_id;
  showOtherMissions.value = true;
  return skipMission(mission);
}

function missionForAgenda(agenda) {
  const missionId = agenda?.next_mission_id;
  if (!missionId) return null;

  return localizedMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, missionId);
  }) || null;
}

function doneForTodayAgendaNarrative() {
  return {
    message: t("missions.agendaNarrative.doneForToday"),
    mood: "sleeping",
  };
}

function isAgendaMissionReachable(mission, actionType) {
  if (!mission?.mission_id) return false;

  if (actionType === "optional_mission") {
    return !!(
      optionalNextMission.value
      && sameMissionId(mission.mission_id, optionalNextMission.value.mission_id)
    );
  }

  if (sameMissionId(mission.mission_id, focusMission.value?.mission_id)) {
    return showFocusMissionCard.value && !missionHasStatus(mission, "done", "locked");
  }

  if (optionalNextMission.value && sameMissionId(mission.mission_id, optionalNextMission.value.mission_id)) {
    return true;
  }

  return otherMissions.value.some((item) => {
    return sameMissionId(item.mission_id, mission.mission_id)
      && !missionHasStatus(item, "done", "locked");
  });
}

function missionForGuidanceAction(action) {
  const actionMissionId = action?.mission_id;
  if (actionMissionId) {
    const matchingMission = localizedMissions.value.find((mission) => mission.mission_id === actionMissionId);
    if (matchingMission) return matchingMission;
  }

  if (focusMission.value?.mission_id) {
    const matchingFocus = localizedMissions.value.find((mission) => mission.mission_id === focusMission.value.mission_id);
    return matchingFocus || focusMission.value;
  }

  return null;
}

function isTinyMission(mission) {
  return mission?.mission_intensity === "tiny";
}

function normalizedMissionIntensity(mission) {
  const intensity = mission?.mission_intensity || "main";

  return ["main", "tiny", "bonus"].includes(intensity) ? intensity : "main";
}

function missionEstimatedMinutes(mission) {
  const minutes = Number(mission?.estimated_minutes);

  return Number.isFinite(minutes) && minutes > 0 ? Math.round(minutes) : null;
}

function normalizedMissionDifficulty(mission) {
  const difficulty = String(mission?.difficulty || "easy").trim().toLowerCase();

  return ["easy", "medium", "hard"].includes(difficulty) ? difficulty : "easy";
}

function missionMetadataChips(mission) {
  if (!mission) return [];

  const chips = [];
  const minutes = missionEstimatedMinutes(mission);

  if (minutes) {
    chips.push({
      key: "minutes",
      type: "minutes",
      label: t("missions.metadata.minutes", { count: minutes }),
    });
  }

  chips.push({
    key: "difficulty",
    type: `difficulty ${normalizedMissionDifficulty(mission)}`,
    label: t(`missions.metadata.difficulty.${normalizedMissionDifficulty(mission)}`),
  });

  return chips;
}

function buildMissionIntensityMeta(mission, options = {}) {
  if (!mission) return null;

  const rawIntensity = String(mission?.mission_intensity || "").trim().toLowerCase();
  const intensity = ["main", "tiny", "bonus"].includes(rawIntensity) ? rawIntensity : "mission";
  const optionalContext = Boolean(options.optionalContext);
  const labelKey = optionalContext && intensity === "main"
    ? "missions.intensity.optional"
    : `missions.intensity.${intensity}`;
  const detailKey = optionalContext && intensity === "main"
    ? "missions.intensity.optionalDetail"
    : `missions.intensity.${intensity}Detail`;
  const detailParts = [t(detailKey)];
  const minutes = missionEstimatedMinutes(mission);

  if (minutes) {
    detailParts.push(t("missions.intensity.minutes", { count: minutes }));
  }

  return {
    intensity,
    label: t(labelKey),
    detail: detailParts.filter(Boolean).join(" · "),
  };
}

function parentMissionFor(mission) {
  if (!mission?.parent_mission_id) return null;

  return localizedMissions.value.find((item) => {
    return sameMissionId(item.mission_id, mission.parent_mission_id);
  }) || null;
}

function childMissionsFor(mission) {
  if (!mission?.mission_id) return [];

  return localizedMissions.value.filter((item) => {
    return sameMissionId(item.parent_mission_id, mission.mission_id);
  });
}

function hasDoneTinyChild(mission) {
  return childMissionsFor(mission).some((item) => {
    return isTinyMission(item) && missionHasStatus(item, "done");
  });
}

function hasRepresentativeTinyChild(mission) {
  return childMissionsFor(mission).some((item) => {
    return isTinyMission(item)
      && isTinyMissionRevealed(item)
      && missionHasStatus(item, "done", "remind_later");
  });
}

function isFocusedTinyChildOf(mission) {
  return !!(
    mission?.mission_id
    && isTinyMission(focusMission.value)
    && sameMissionId(focusMission.value?.parent_mission_id, mission.mission_id)
  );
}

function isTinyMissionRevealed(mission) {
  return !!(
    mission?.mission_id
    && revealedTinyMissionIds.value.has(String(mission.mission_id))
  );
}

function preferMainMissionAfterReminder(mission) {
  if (!mission?.mission_id || normalizedMissionIntensity(mission) !== "main") return;

  const childTinyMissionIds = childMissionsFor(mission)
    .filter(isTinyMission)
    .map((item) => String(item.mission_id));

  if (!childTinyMissionIds.length) return;

  revealedTinyMissionIds.value = new Set(
    [...revealedTinyMissionIds.value].filter((missionId) => {
      return !childTinyMissionIds.includes(String(missionId));
    }),
  );
}

function missionGroupRootId(mission) {
  if (!mission?.mission_id) return "";

  if (normalizedMissionIntensity(mission) === "bonus") {
    return String(mission.mission_id);
  }

  return String(mission.parent_mission_id || mission.mission_id);
}

function sameMissionGroup(a, b) {
  const aRoot = missionGroupRootId(a);
  const bRoot = missionGroupRootId(b);

  return !!(aRoot && bRoot && aRoot === bRoot);
}

function shouldShowOtherMission(mission) {
  if (!mission?.mission_id) return false;
  if (sameMissionId(mission.mission_id, focusMission.value?.mission_id) && isFocusMissionRendered()) return true;

  const intensity = normalizedMissionIntensity(mission);
  const parentMission = parentMissionFor(mission);

  const mainHasExplicitState = missionHasStatus(mission, "remind_later", "done", "skipped")
    || sameMissionId(mission.mission_id, manualFocusMissionId.value);

  if (
    intensity === "main"
    && !mainHasExplicitState
    && (hasRepresentativeTinyChild(mission) || isFocusedTinyChildOf(mission))
  ) {
    return false;
  }

  if (intensity === "tiny") {
    if (missionHasStatus(mission, "done", "remind_later")) return true;
    if (!isTinyMissionRevealed(mission)) return false;
    if (parentMission && missionHasStatus(parentMission, "done") && missionHasStatus(mission, "pending")) {
      return false;
    }
    return true;
  }

  if (intensity === "bonus" && !isTodaySaved.value && missionHasStatus(mission, "pending")) {
    return false;
  }

  return true;
}

function shouldShowOtherMissionItem(mission) {
  if (!mission?.mission_id) return false;
  if (isTodaySaved.value && missionHasStatus(mission, "pending")) return false;

  return true;
}

function shouldShowOptionalExplorerMission(mission) {
  if (!mission?.mission_id) return false;
  if (missionHasStatus(mission, "locked")) return false;
  if (isFocusMissionRendered() && sameMissionId(mission.mission_id, focusMission.value?.mission_id)) return false;

  return missionHasStatus(mission, "pending", "remind_later", "done", "skipped");
}

function isFocusMissionRendered() {
  if (!focusMission.value) return false;
  if (missionHasStatus(focusMission.value, "remind_later")) {
    return isReminderDue(focusMission.value) || !!(
      sameMissionId(focusMission.value.mission_id, manualFocusMissionId.value)
      || isReminderPanelOpen(focusMission.value)
      || isSkipReasonPanelOpen(focusMission.value)
    );
  }
  if (!isTodaySaved.value) return true;
  if (missionHasStatus(focusMission.value, "done")) return false;

  return !!(
    sameMissionId(focusMission.value.mission_id, manualFocusMissionId.value)
    || isReminderPanelOpen(focusMission.value)
    || isSkipReasonPanelOpen(focusMission.value)
  );
}

function primaryReminderMission() {
  return sortReminderMissions(
    effectiveMissionRepresentatives.value.filter((mission) => {
      return missionHasStatus(mission, "remind_later") && isReminderDue(mission);
    }),
  )[0] || null;
}

function missionItemIntensity(mission) {
  return buildMissionIntensityMeta(mission, {
    optionalContext: isTodaySaved.value,
  });
}

function missionTypeLabel(mission) {
  const intensity = normalizedMissionIntensity(mission);

  if (intensity === "main") return t("missions.typeChips.main");
  if (intensity === "tiny") return t("missions.typeChips.tiny");
  if (intensity === "bonus") return t("missions.typeChips.bonus");

  return t("missions.typeChips.main");
}

function missionChips(mission) {
  if (!mission) return [];

  const status = normalizedMissionStatus(mission.status);
  const knownStatus = ["pending", "done", "skipped", "remind_later"].includes(status)
    ? status
    : "pending";

  return [
    {
      key: "type",
      type: normalizedMissionIntensity(mission),
      label: missionTypeLabel(mission),
    },
    {
      key: "status",
      type: knownStatus,
      label: t(`missions.status.${knownStatus}`),
    },
  ];
}

function missionParentCopy(mission) {
  const parentMission = parentMissionFor(mission);
  if (!parentMission) return "";

  return t("missions.variantOf", { mission: parentMission.title });
}

function optionalMissionRank(mission, focusChallengeId) {
  const intensity = normalizedMissionIntensity(mission);
  const isDifferentChallenge = !sameMissionId(mission?.challenge_id, focusChallengeId);

  if (intensity === "main" && isDifferentChallenge) return 0;
  if (intensity === "main") return 1;
  if (intensity === "bonus" && isDifferentChallenge) return 2;
  if (intensity === "bonus") return 3;
  if (isDifferentChallenge) return 4;

  return 5;
}

function normalizedMissionStatus(status) {
  const value = String(status || "pending")
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, "_");

  if (["done", "complete", "completed"].includes(value)) return "done";
  if (["skipped", "skip"].includes(value)) return "skipped";
  if (["remind_later", "reminder_set", "reminded"].includes(value)) return "remind_later";

  return value || "pending";
}

function missionHasStatus(mission, ...statuses) {
  const normalized = normalizedMissionStatus(mission?.status);

  return statuses.includes(normalized);
}

function missionStatusLabel(mission) {
  const status = normalizedMissionStatus(mission?.status);
  const knownStatus = ["pending", "done", "skipped", "remind_later", "locked"].includes(status)
    ? status
    : "pending";

  return t(`missions.status.${knownStatus}`);
}

function formattedReminderTime(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat(locale.value || undefined, {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function parsedDate(value) {
  if (!value) return null;

  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function formattedTimelineTime(value) {
  const date = parsedDate(value);
  if (!date) return "";

  return new Intl.DateTimeFormat(locale.value || undefined, {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function isWithinTimelineBounds(date) {
  const parsed = parsedDate(date);
  if (!parsed) return false;

  return parsed.getTime() >= timelineBounds.value.start.getTime()
    && parsed.getTime() <= timelineBounds.value.end.getTime();
}

function timelinePositionForDate(value) {
  const dateValue = parsedDate(value) || new Date();
  const start = timelineBounds.value.start.getTime();
  const end = timelineBounds.value.end.getTime();
  const span = Math.max(end - start, 1);
  const raw = ((dateValue.getTime() - start) / span) * 100;

  return Math.min(100, Math.max(0, raw));
}

function timelineClusterFromItems(items) {
  const primary = items[0];
  const statuses = [...new Set(items.map((item) => item.status))];
  const types = [...new Set(items.map((item) => item.type))];
  const totalPosition = items.reduce((sum, item) => sum + item.position, 0);
  const position = totalPosition / Math.max(items.length, 1);
  const markerStatus = statuses.length === 1 ? statuses[0] : "mixed";
  const markerType = types.length === 1 ? types[0] : "mixed";
  const title = items.length > 1
    ? t("missions.timeline.clusterTitle", { count: items.length })
    : primary.mission.title;
  const meta = items.length > 1
    ? items.map((item) => item.mission.title).slice(0, 2).join(" · ")
    : primary.meta;
  const ariaLabel = items.length > 1
    ? `${title}: ${meta}`
    : `${primary.timeLabel}: ${primary.mission.title}, ${primary.meta}`;
  const xp = timelineClusterXp(items, position, markerStatus);

  return {
    key: items.map((item) => item.key).join("|"),
    position,
    timeLabel: primary.timeLabel,
    title,
    meta,
    primary,
    markerStatus,
    markerType,
    markerStatusClass: `status-${markerStatus}`,
    markerTypeClass: `type-${markerType}`,
    nearReset: position >= 92 && !["done", "skipped"].includes(markerStatus),
    ariaLabel,
    typeSummary: types.slice(0, 3),
    xp,
    items,
  };
}

function missionXpMeta(mission, options = {}) {
  if (!mission) return null;

  const earned = Number(mission.xp_earned || 0);
  const reward = Number(mission.xp_reward || 0);
  const amount = Math.max(earned, reward);

  if (!Number.isFinite(amount) || amount <= 0) return null;

  let state = "available";
  if (missionHasStatus(mission, "done")) state = "earned";
  if (missionHasStatus(mission, "skipped")) state = "inactive";
  if (missionHasStatus(mission, "remind_later")) state = "reminder";
  if (options.nearReset && !missionHasStatus(mission, "done", "skipped")) state = "danger";

  return {
    label: t("common.xp", { count: amount }),
    state,
  };
}

function timelineClusterXp(items, position, markerStatus) {
  const total = items.reduce((sum, item) => {
    const earned = Number(item.mission.xp_earned || 0);
    const reward = Number(item.mission.xp_reward || 0);
    const amount = Math.max(earned, reward);

    return Number.isFinite(amount) ? sum + amount : sum;
  }, 0);

  if (total <= 0) return null;

  let state = "available";
  if (markerStatus === "done") state = "earned";
  if (markerStatus === "skipped") state = "inactive";
  if (markerStatus === "remind_later") state = "reminder";
  if (position >= 92 && !["done", "skipped"].includes(markerStatus)) state = "danger";

  return {
    label: t("common.xp", { count: total }),
    state,
  };
}

function missionMarkerClasses(mission, options = {}) {
  const type = normalizedMissionIntensity(mission);
  const status = normalizedMissionStatus(mission?.status);
  const markerStatus = ["pending", "done", "skipped", "remind_later"].includes(status)
    ? status
    : "pending";

  return [
    `type-${type}`,
    `status-${markerStatus}`,
    {
      nearReset: options.nearReset,
    },
  ];
}

function missionTimelineTimestamp(mission) {
  const status = normalizedMissionStatus(mission?.status);
  const candidates = [];

  if (status === "remind_later" && mission?.reminder_at) {
    candidates.push(mission?.reminder_at);
  }

  if (status === "done") {
    candidates.push(
      mission?.done_at,
      mission?.completed_at,
      mission?.secured_at,
      mission?.status_at,
      mission?.status_updated_at,
    );
  }

  if (status === "skipped") {
    candidates.push(
      mission?.skipped_at,
      mission?.status_at,
      mission?.status_updated_at,
    );
  }

  const timestamp = candidates
    .map(parsedDate)
    .find((date) => date && isWithinTimelineBounds(date));

  return timestamp || null;
}

function timelineMissionTimeLabel(mission) {
  const timestamp = missionTimelineTimestamp(mission);
  return timestamp ? formattedTimelineTime(timestamp) : "";
}

function selectTimelineMission(mission) {
  if (!mission?.mission_id) return;

  selectedTimelineMissionId.value = mission.mission_id;
}

function selectTimelineCluster(cluster) {
  const selectedItem = cluster?.items?.find((item) => {
    return isTimelineMissionSelected(item.mission);
  }) || cluster?.items?.[0];

  if (selectedItem?.mission) {
    selectTimelineMission(selectedItem.mission);
  }
}

function isTimelineMissionSelected(mission) {
  return !!(
    mission?.mission_id
    && sameMissionId(mission.mission_id, selectedTimelineMissionId.value)
  );
}

function parsedNextResetAt() {
  const value = guidanceRingoDay.value?.next_reset_at;
  if (!value) return null;

  const reset = new Date(value);
  return Number.isNaN(reset.getTime()) ? null : reset;
}

function isAfterNextRingoReset(value) {
  const reset = parsedNextResetAt();
  if (!reset) return false;

  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return false;

  return date.getTime() >= reset.getTime();
}

function isTomorrowLocalDate(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return false;

  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);

  return date.getFullYear() === tomorrow.getFullYear()
    && date.getMonth() === tomorrow.getMonth()
    && date.getDate() === tomorrow.getDate();
}

function reminderTomorrowSlotKey(date) {
  if (!isTomorrowLocalDate(date)) return "";

  const hour = date.getHours();
  const minute = date.getMinutes();

  if (hour === 18 && minute === 0) return "evening";
  if (hour === 22 && minute === 0) return "night";

  return "default";
}

function formattedReminderLabel(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  const time = formattedReminderTime(value);
  const tomorrowSlot = reminderTomorrowSlotKey(date);

  if (isAfterNextRingoReset(date)) {
    return t("missions.remindOptions.afterReset", { time });
  }

  if (tomorrowSlot === "evening") {
    return t("missions.remindOptions.tomorrowEveningAt", { time });
  }

  if (tomorrowSlot === "night") {
    return t("missions.remindOptions.tomorrowNightAt", { time });
  }

  if (tomorrowSlot === "default") {
    return t("missions.remindOptions.tomorrowAt", { time });
  }

  return time;
}

function formattedReminderSummaryLabel(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  const label = formattedReminderLabel(value);
  if (!label) return "";

  if (isAfterNextRingoReset(date)) {
    return t("missions.remindOptions.afterResetAt", { time: formattedReminderTime(value) });
  }

  return reminderTomorrowSlotKey(date)
    ? label
    : t("missions.remindOptions.atTime", { time: label });
}

function reminderTimestamp(mission) {
  if (!mission?.reminder_at) return Number.POSITIVE_INFINITY;

  const date = new Date(mission.reminder_at);
  const timestamp = date.getTime();

  return Number.isNaN(timestamp) ? Number.POSITIVE_INFINITY : timestamp;
}

function isReminderDue(mission) {
  return reminderTimestamp(mission) <= Date.now();
}

function isFutureReminder(mission) {
  return missionHasStatus(mission, "remind_later") && reminderTimestamp(mission) > Date.now();
}

function optionalActionableCount(stats = {}) {
  return Number(stats.pending || 0);
}

function optionalGroupNarrativeCount(stats = {}) {
  if (optionalGroupHasOnlyFutureReminders(stats)) return Number(stats.futureReminders || 0);
  return optionalActionableCount(stats);
}

function optionalGroupIsCompleteForNow(stats = {}) {
  return Number(stats.total || 0) > 0
    && Number(stats.percent || 0) >= 100
    && !Number(stats.pending || 0)
    && !Number(stats.reminderDue || 0)
    && !Number(stats.futureReminders || 0)
    && !Number(stats.skipped || 0);
}

function optionalGroupHasOnlyFutureReminders(stats = {}) {
  return !Number(stats.pending || 0)
    && !Number(stats.reminderDue || 0)
    && Number(stats.futureReminders || 0) > 0
    && !Number(stats.skipped || 0);
}

function optionalPathNarrativeKey(stats = {}) {
  if (optionalGroupIsCompleteForNow(stats)) return "missions.narrative.optionalPathComplete";
  if (optionalGroupHasOnlyFutureReminders(stats)) return "missions.narrative.optionalPathFutureReminders";

  const count = optionalActionableCount(stats);
  if (count === 1) return "missions.narrative.optionalPathOneStep";
  if (count > 1) return "missions.narrative.optionalPathManySteps";
  if (Number(stats.done || 0) > 0) return "missions.narrative.optionalPathPartial";

  return "missions.narrative.optionalPathSelected";
}

function optionalChallengeNarrativeKey(stats = {}) {
  if (optionalGroupIsCompleteForNow(stats)) return "missions.narrative.optionalChallengeComplete";
  if (optionalGroupHasOnlyFutureReminders(stats)) return "missions.narrative.optionalChallengeFutureReminders";

  const count = optionalActionableCount(stats);
  if (count === 1) return "missions.narrative.optionalChallengeOneStep";
  if (count > 1) return "missions.narrative.optionalChallengeManySteps";
  if (Number(stats.done || 0) > 0) return "missions.narrative.optionalChallengePartial";

  return "missions.narrative.optionalChallengeSelected";
}

function selectedOptionalExplorerNarrativeKey(mission) {
  if (missionHasStatus(mission, "remind_later")) {
    return isReminderDue(mission)
      ? "missions.narrative.optionalSelectedDueReminder"
      : "missions.narrative.optionalSelectedFutureReminder";
  }

  if (missionHasStatus(mission, "done")) return "missions.narrative.optionalSelectedDone";
  if (missionHasStatus(mission, "skipped")) return "missions.narrative.optionalSelectedSkipped";

  return "missions.narrative.optionalSelectedPending";
}

function selectedOptionalExplorerNarrativeMood(mission) {
  if (missionHasStatus(mission, "remind_later")) {
    return isReminderDue(mission) ? "thinking" : "sleeping";
  }

  if (missionHasStatus(mission, "done")) return "proud";
  if (missionHasStatus(mission, "skipped")) return "concerned";

  return "happy";
}

function sortReminderMissions(items) {
  return [...items].sort((a, b) => {
    const aDue = isReminderDue(a);
    const bDue = isReminderDue(b);

    if (aDue !== bDue) return aDue ? -1 : 1;

    return reminderTimestamp(a) - reminderTimestamp(b);
  });
}

function reminderDeliveryMeta(mission) {
  if (!mission || normalizedMissionStatus(mission.status) !== "remind_later") return null;

  if (mission.reminder_sent_at) {
    return {
      state: "sent",
      label: t("missions.reminderDelivery.sent"),
    };
  }

  if (isReminderDue(mission)) {
    return {
      state: "due",
      label: t("missions.reminderDelivery.due"),
    };
  }

  if (!telegramConnected.value) {
    return {
      state: "needsConnection",
      label: t("missions.reminderDelivery.telegramNotConnected"),
    };
  }

  if (!telegramRemindersEnabled.value) {
    return {
      state: "disabled",
      label: t("missions.reminderDelivery.telegramDisabled"),
    };
  }

  return {
    state: "scheduled",
    label: t("missions.reminderDelivery.scheduled"),
  };
}

function missionStatusCopy(mission) {
  if (!mission) return "";

  const status = normalizedMissionStatus(mission.status);

  if (status === "skipped") {
    if (normalizedMissionIntensity(mission) === "bonus") {
      return t("missions.statusCopy.bonusSkipped");
    }

    return t("missions.statusCopy.skipped");
  }

  if (status === "remind_later") {
    const time = formattedReminderLabel(mission.reminder_at);
    if (isReminderDue(mission)) {
      return time
        ? t("missions.statusCopy.reminderDueWithTime", { time })
        : t("missions.statusCopy.reminderDue");
    }

    return time
      ? t("missions.statusCopy.reminderWithTime", { time })
      : t("missions.statusCopy.reminder");
  }

  if (status === "done") {
    return t("missions.statusCopy.done");
  }

  if (status === "pending" && normalizedMissionIntensity(mission) === "bonus") {
    return t("missions.statusCopy.bonusPending");
  }

  if (
    status === "pending"
    && normalizedMissionIntensity(mission) === "main"
    && hasDoneTinyChild(mission)
  ) {
    return t("missions.statusCopy.optionalUpgrade");
  }

  return mission.ringo_message || "";
}

function missionReminderContextLabel(mission) {
  if (!mission?.reminder_at) return "";
  return formattedReminderLabel(mission.reminder_at);
}

function isPendingTinyMission(mission) {
  return isTinyMission(mission) && missionHasStatus(mission, "pending");
}

function sameMissionId(a, b) {
  if (a === null || a === undefined || b === null || b === undefined) return false;

  return String(a) === String(b);
}

function findTinyMissionFor(mission) {
  if (isPendingTinyMission(mission)) return mission;

  if (mission?.mission_id) {
    const linkedTinyMission = linkedTinyMissionFor(mission);

    if (linkedTinyMission) return linkedTinyMission;
  }

  return null;
}

function linkedTinyMissionFor(mission) {
  if (!mission?.mission_id) return null;

  return localizedMissions.value.find((item) => {
    return isPendingTinyMission(item) && sameMissionId(item.parent_mission_id, mission.mission_id);
  }) || null;
}

function isGuidanceActionDisabled(action) {
  const mission = missionForGuidanceAction(action);

  if (action.type === "make_smaller" || action.type === "too_tired") return false;
  if (!mission) return action.type !== "make_smaller" && action.type !== "too_tired";
  if (missionHasStatus(mission, "done")) return true;
  if (action.type === "skip_today") return missionHasStatus(mission, "skipped");

  return false;
}

function guidanceActionByType(type) {
  return guidanceActions.value.find((action) => action.type === type) || null;
}

function guidanceActionForMission(type, mission) {
  return guidanceActionByType(type) || {
    type,
    mission_id: mission?.mission_id,
  };
}

function shouldShowFocusSupportAction(type, mission) {
  if (!["make_smaller", "too_tired"].includes(type)) return false;
  if (!mission || missionHasStatus(mission, "done", "skipped", "remind_later")) return false;
  if (normalizedMissionIntensity(mission) !== "main") return false;
  if (!linkedTinyMissionFor(mission)) return false;

  const action = guidanceActionForMission(type, mission);
  if (isGuidanceActionDisabled(action)) return false;

  return true;
}

function handleFocusSupportAction(type, mission) {
  handleGuidanceAction(guidanceActionForMission(type, mission));
}

function shouldShowOptionalNextSupportAction(type, mission) {
  if (!["make_smaller", "too_tired"].includes(type)) return false;
  if (!mission || normalizedMissionIntensity(mission) !== "main") return false;
  if (missionHasStatus(mission, "done", "skipped", "remind_later")) return false;

  return !!linkedTinyMissionFor(mission);
}

function handleOptionalNextSupportAction(type, mission) {
  if (!shouldShowOptionalNextSupportAction(type, mission)) return;

  focusTinyMissionFromAction(
    {
      type,
      mission_id: mission.mission_id,
    },
    type === "too_tired"
      ? "missions.ringoActions.tooTiredTinyMessage"
      : "missions.ringoActions.makeSmallerTinyMessage",
    type === "too_tired"
      ? "missions.ringoActions.tooTiredMessage"
      : "missions.ringoActions.makeSmallerMessage",
  );
}

function shouldShowMissionItemTinyAction(mission) {
  if (!mission || normalizedMissionIntensity(mission) !== "main") return false;
  if (!missionHasStatus(mission, "pending", "remind_later", "skipped")) return false;

  return !!linkedTinyMissionFor(mission);
}

function focusTinyMissionVariant(mission) {
  if (!shouldShowMissionItemTinyAction(mission)) return;

  focusTinyMissionFromAction(
    {
      type: "make_smaller",
      mission_id: mission.mission_id,
    },
    "missions.ringoActions.makeSmallerTinyMessage",
    "missions.ringoActions.makeSmallerMessage",
  );
}

function shouldShowFullVersionAction(mission) {
  if (!mission || normalizedMissionIntensity(mission) !== "tiny") return false;

  const parentMission = parentMissionFor(mission);
  return !!(
    parentMission
    && !missionHasStatus(parentMission, "done", "locked")
  );
}

function focusMainMissionVariant(mission) {
  if (!shouldShowFullVersionAction(mission)) return;

  const parentMission = parentMissionFor(mission);
  revealedTinyMissionIds.value = new Set(
    [...revealedTinyMissionIds.value].filter((missionId) => {
      return !sameMissionId(missionId, mission.mission_id);
    }),
  );
  manualFocusMissionId.value = parentMission.mission_id;
  reminderPanelMissionId.value = null;
  customReminderPanelMissionId.value = null;
  customReminderTime.value = "";
  skipReasonPanelMissionId.value = null;
  setInteractionNarrative("missions.ringoActions.useFullVersionMessage", "encouraging", {
    mission: parentMission.title,
  });
  focusMissionCard(parentMission);
}

function showMissionItemActions(mission) {
  return !!(
    mission
    && !isReminderPanelOpen(mission)
    && !isSkipReasonPanelOpen(mission)
  );
}

function focusTinyMissionFromAction(action, messageKey, fallbackMessageKey) {
  const mission = missionForGuidanceAction(action);
  const tinyMission = findTinyMissionFor(mission);

  if (!tinyMission) {
    setInteractionNarrative(fallbackMessageKey, action.type === "too_tired" ? "sleeping" : "thinking");
    return;
  }

  revealedTinyMissionIds.value = new Set([
    ...revealedTinyMissionIds.value,
    String(tinyMission.mission_id),
  ]);
  manualFocusMissionId.value = tinyMission.mission_id;
  setInteractionNarrative(messageKey, action.type === "too_tired" ? "sleeping" : "encouraging", {
    mission: tinyMission.title,
  });
  focusMissionCard(tinyMission);
  completeFirstRunFocus();
}

function handleGuidanceAction(action) {
  const mission = missionForGuidanceAction(action);

  if (action.type === "make_smaller") {
    focusTinyMissionFromAction(
      action,
      "missions.ringoActions.makeSmallerTinyMessage",
      "missions.ringoActions.makeSmallerMessage",
    );
    return;
  }

  if (action.type === "too_tired") {
    focusTinyMissionFromAction(
      action,
      "missions.ringoActions.tooTiredTinyMessage",
      "missions.ringoActions.tooTiredMessage",
    );
    return;
  }

  if (!mission) return;

  if (action.type === "remind_later") {
    remindLater(mission);
    return;
  }

  if (action.type === "skip_today") {
    skipMission(mission);
    return;
  }

  focusMissionCard(mission);
}

async function focusMissionCard(mission) {
  await nextTick();
  document
    .getElementById(`mission-${mission.mission_id}`)
    ?.scrollIntoView({ behavior: "smooth", block: "center" });
}

function handleCoachAction(action) {
  if (action?.type === "dismiss") {
    dismissedCoachState.value = ringo.value?.state || "";
    return;
  }

  if (!action?.mission_id) return;

  const mission = localizedMissions.value.find((item) => item.mission_id === action.mission_id);

  if (!mission) return;

  if (action.type === "mission_reminder") {
    remindLater(mission);
    return;
  }

  markDone(mission);
}

watch(
  missionFocusState,
  (state) => {
    emit("focus-state-change", state);
  },
  { immediate: true },
);

watch(
  () => props.focusModeActive,
  (active) => {
    if (active) {
      missionStatusExpanded.value = false;
    }
  },
);

onMounted(loadMissions);
</script>

<style scoped>
.missionActionButton {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.missionActionIcon {
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  display: block;
  object-fit: contain;
  margin-inline-end: 7px;
  filter: brightness(0) invert(1);
  opacity: 0.86;
}

.missionActionButtonPrimary .missionActionIcon {
  filter: brightness(0) invert(1) drop-shadow(0 0 10px rgba(110, 229, 255, 0.18));
}


.missionCenter {
  display: grid;
  gap: var(--s-16);
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow-x: clip;
}

.missionCenter.hasDailyMomentumBar {
  padding-bottom: 104px;
}

@media (max-width: 880px) {
  .missionCenter.hasDailyMomentumBar {
    padding-bottom: 176px;
  }
}

.missionList {
  display: grid;
  gap: var(--s-16);
  min-width: 0;
  max-width: 100%;
}

.restModeCard {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  width: 100%;
  gap: var(--s-20);
  align-items: center;
  min-height: 360px;
  padding: 28px;
  border-color: rgba(110, 229, 255, 0.13);

  background:
    radial-gradient(circle at 16% 18%, rgba(110, 229, 255, 0.12), transparent 30%),
    radial-gradient(circle at 84% 0%, rgba(74, 222, 128, 0.08), transparent 32%),
    rgba(255, 255, 255, 0.028);
}

.restModeCard::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.restModeSprite,
.restModeCopy,
.restModeActions {
  position: relative;
  z-index: 1;
}

.restModeSprite {
  display: grid;
  place-items: center;
  width: clamp(128px, 20vw, 210px);
  aspect-ratio: 1;
  border-radius: 32px;
  background: rgba(0, 0, 0, 0.16);
}

.restModeSprite img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.restModeCopy {
  display: grid;
  gap: 10px;
}

.restModeCopy h2,
.restModeCopy p {
  margin: 0;
}

.restModeCopy h2 {
  color: rgba(255, 255, 255, 0.96);
  font-size: clamp(1.8rem, 4vw, 3.2rem);
  line-height: 1;
  letter-spacing: -0.045em;
}

.restModeCopy p:not(.eyebrow) {
  max-width: 560px;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.7;
}

.restModeReminder {
  width: fit-content;
  padding: 9px 12px;
  border-radius: 999px;
  color: rgba(187, 247, 208, 0.94);
  background: rgba(74, 222, 128, 0.08);
  border: 1px solid rgba(74, 222, 128, 0.16);
  font-size: 0.84rem;
  font-weight: 800;
}

.restModeActions {
  grid-column: 2;
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
}

.missionStatusToggle {
  display: flex;
  justify-content: center;
}

.secondaryMissionList {
  gap: var(--s-12);
  border-color: rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.028);
}

.coachActionPanel {
  display: grid;
  gap: var(--s-12);
  border-color: rgba(110, 229, 255, 0.16);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.10), transparent 32%),
    rgba(255, 255, 255, 0.035);
}

.coachActionPanel.complete {
  border-color: rgba(74, 222, 128, 0.22);
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.10), transparent 32%),
    rgba(255, 255, 255, 0.035);
}

.firstRunRevealPanel .firstRunRevealStep {
  opacity: 0;
  transform: translateY(8px);
  animation: firstRunRevealStep 420ms cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

.firstRunRevealPanel .firstRunRevealCoach {
  animation-delay: 200ms;
}

.firstRunRevealPanel .firstRunRevealIntro {
  animation-delay: 3000ms;
}

.firstRunRevealPanel .firstRunRevealMission {
  animation-delay: 7000ms;
}

.firstRunRevealPanel .firstRunRevealEducation {
  animation-delay: 8500ms;
}

@keyframes firstRunRevealStep {
  from {
    opacity: 0;
    transform: translateY(8px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.missionGuide {
  display: grid;
  gap: var(--s-16);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.12), transparent 36%),
    radial-gradient(circle at 100% 0%, rgba(247, 215, 116, 0.10), transparent 30%),
    rgba(255, 255, 255, 0.04);
}

.missionGuide.complete {
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.12), transparent 34%),
    rgba(255, 255, 255, 0.035);
}

.missionGuide.skipped {
  border-color: rgba(255, 255, 255, 0.14);
  background:
    radial-gradient(circle at 0% 0%, rgba(255, 255, 255, 0.08), transparent 34%),
    rgba(255, 255, 255, 0.032);
}

.missionGuide.reminder {
  border-color: rgba(247, 215, 116, 0.20);
  background:
    radial-gradient(circle at 0% 0%, rgba(247, 215, 116, 0.10), transparent 34%),
    rgba(255, 255, 255, 0.032);
}

.missionGuideCopy h2,
.missionGuideCopy p,
.focusMission p {
  margin: 0;
}

.missionGuideCopy h2 {
  color: rgba(255, 255, 255, 0.96);
  letter-spacing: -0.04em;
}

.missionGuideCopy p {
  margin-top: 8px;
  max-width: 760px;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.65;
}

.missionStepper {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-8);
}

.step {
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.62);
  background: rgba(255, 255, 255, 0.035);
  font-size: var(--cap);
  font-weight: 850;
  text-align: center;
}

.step.complete {
  border-color: rgba(74, 222, 128, 0.24);
  color: rgba(187, 247, 208, 0.95);
  background: rgba(74, 222, 128, 0.07);
}

.step.active {
  border-color: rgba(247, 215, 116, 0.30);
  color: rgba(253, 230, 138, 0.96);
  background: rgba(247, 215, 116, 0.08);
  box-shadow: 0 0 28px rgba(247, 215, 116, 0.08);
}

.focusMission {
  display: grid;
  gap: 6px;
  padding: 14px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 18px;
  background: rgba(5, 10, 18, 0.26);
}

.coachFocusMission {
  border-color: rgba(110, 229, 255, 0.22);
  background: rgba(5, 10, 18, 0.18);
}

.focusMission span {
  color: rgba(110, 229, 255, 0.82);
  font-size: var(--cap);
  font-weight: 900;
}

.focusMission strong {
  color: rgba(255, 255, 255, 0.94);
}

.focusMission p {
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.missionIntensity {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  width: fit-content;
  max-width: 100%;
  padding: 5px 8px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.95);
  background: rgba(110, 229, 255, 0.07);
  font-size: var(--cap);
  font-weight: 850;
  line-height: 1.25;
}

.missionIntensity.tiny {
  border-color: rgba(74, 222, 128, 0.24);
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.075);
}

.missionIntensity.bonus {
  border-color: rgba(247, 215, 116, 0.26);
  color: rgba(253, 230, 138, 0.96);
  background: rgba(247, 215, 116, 0.075);
}

.missionIntensity span,
.missionIntensity small {
  min-width: 0;
  color: inherit;
  font: inherit;
}

.missionIntensity small {
  opacity: 0.78;
}

.missionStatusCopy {
  display: block;
  margin-top: 2px;
  color: rgba(247, 215, 116, 0.82);
  font-size: 0.86rem;
  font-weight: 720;
  line-height: 1.5;
}

.reminderDeliveryChip {
  display: inline-flex;
  width: fit-content;
  margin-top: 6px;
  padding: 5px 8px;
  border: 1px solid rgba(247, 215, 116, 0.22);
  border-radius: 999px;
  color: rgba(253, 230, 138, 0.92);
  background: rgba(247, 215, 116, 0.075);
  font-size: 0.76rem;
  font-weight: 850;
  line-height: 1.2;
}

.reminderDeliveryChip.sent {
  border-color: rgba(74, 222, 128, 0.24);
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.075);
}

.reminderDeliveryChip.due {
  border-color: rgba(110, 229, 255, 0.24);
  color: rgba(219, 244, 255, 0.96);
  background: rgba(110, 229, 255, 0.075);
}

.reminderDeliveryChip.needsConnection,
.reminderDeliveryChip.disabled {
  border-color: rgba(251, 146, 60, 0.24);
  color: rgba(254, 215, 170, 0.96);
  background: rgba(251, 146, 60, 0.075);
}

.todaySaved {
  display: grid;
  gap: 4px;
  margin: 0;
  padding: 11px 13px;
  border: 1px solid rgba(74, 222, 128, 0.24);
  border-radius: 16px;
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.075);
  font-weight: 850;
}

.todaySaved strong,
.todaySaved span {
  min-width: 0;
}

.todaySaved span {
  color: rgba(220, 252, 231, 0.74);
  font-weight: 700;
  line-height: 1.5;
}

.completedChoices {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  align-items: center;
}

.optionalExplorerPrompt {
  display: grid;
  gap: var(--s-10);
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  padding: 12px;
  border: 1px solid rgba(110, 229, 255, 0.14);
  border-radius: 18px;
  background: rgba(110, 229, 255, 0.05);
  overflow: hidden;
}

.optionalExplorerActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  align-items: center;
  min-width: 0;
  max-width: 100%;
}

.optionalReminderQueue {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 7px 10px;
  border: 1px solid rgba(110, 229, 255, 0.16);
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.86);
  background: rgba(110, 229, 255, 0.065);
  font-size: var(--cap);
  font-weight: 850;
}

.optionalNextStep {
  display: grid;
  gap: var(--s-10);
  padding: 12px;
  border: 1px solid rgba(247, 215, 116, 0.18);
  border-radius: 18px;
  background: rgba(247, 215, 116, 0.055);
}

.optionalNextCopy h3,
.optionalNextCopy p,
.optionalNextMission p {
  margin: 0;
}

.optionalNextCopy h3 {
  color: rgba(255, 255, 255, 0.94);
  font-size: 1rem;
}

.optionalNextCopy p:not(.eyebrow) {
  margin-top: 5px;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.optionalNextMission {
  display: grid;
  gap: 6px;
  padding: 11px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
  background: rgba(5, 10, 18, 0.20);
}

.optionalNextMission strong {
  color: rgba(255, 255, 255, 0.92);
}

.optionalNextMission p {
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.5;
}

.optionalNextActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  align-items: center;
}

.ringoActionHint {
  margin: 0;
  padding: 11px 13px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 16px;
  color: rgba(219, 244, 255, 0.94);
  background: rgba(110, 229, 255, 0.07);
  font-weight: 780;
  line-height: 1.55;
}

.remindOptionsPanel {
  display: grid;
  gap: var(--s-8);
  margin-top: 4px;
  padding: 11px;
  border: 1px solid rgba(247, 215, 116, 0.22);
  border-radius: 16px;
  background: rgba(247, 215, 116, 0.065);
}

.missionItem .remindOptionsPanel {
  grid-column: 1 / -1;
}

.remindOptionsPanel p {
  margin: 0;
  color: rgba(253, 230, 138, 0.95);
  font-weight: 820;
  line-height: 1.45;
}

.remindOptions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
}

.customReminderPanel {
  display: grid;
  gap: var(--s-8);
  padding-top: 2px;
}

.customReminderPanel label {
  color: rgba(255, 255, 255, 0.82);
  font-size: var(--cap);
  font-weight: 850;
}

.customReminderPanel small {
  color: rgba(255, 255, 255, 0.62);
  font-weight: 720;
  line-height: 1.45;
}

.customReminderControls {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  align-items: center;
}

.customReminderControls input {
  min-height: 42px;
  min-width: 142px;
  padding: 9px 11px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.92);
  background: rgba(0, 0, 0, 0.22);
  font: inherit;
  font-weight: 760;
}

.skipReasonPanel {
  display: grid;
  gap: var(--s-8);
  margin-top: 4px;
  padding: 11px;
  border: 1px solid rgba(255, 255, 255, 0.13);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.045);
}

.missionItem .skipReasonPanel {
  grid-column: 1 / -1;
}

.skipReasonPanel p {
  margin: 0;
  color: rgba(255, 255, 255, 0.76);
  font-weight: 780;
  line-height: 1.45;
}

.skipReasons {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
}

.missionGuideActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-10);
  align-items: center;
}

.missionGuideLink {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 9px 13px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 15px;
  color: rgba(255, 255, 255, 0.86);
  background: rgba(255, 255, 255, 0.055);
  font-weight: 850;
  text-decoration: none;
}

.missionGuideLink:hover {
  border-color: rgba(110, 229, 255, 0.24);
  background: rgba(255, 255, 255, 0.08);
}

.missionNotice {
  margin: 0;
  padding: 11px 13px;
  border: 1px solid rgba(74, 222, 128, 0.24);
  border-radius: 16px;
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.075);
  font-weight: 780;
}

.missionNotice.reminder {
  border-color: rgba(247, 215, 116, 0.24);
  color: rgba(253, 230, 138, 0.96);
  background: rgba(247, 215, 116, 0.075);
}

.missionNotice.muted {
  border-color: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.045);
}

.telegramReminderPrompt {
  display: grid;
  gap: var(--s-12);
  padding: 14px;
  border-color: rgba(110, 229, 255, 0.16);
  background: rgba(110, 229, 255, 0.055);
}

.telegramReminderPrompt.disabled {
  border-color: rgba(247, 215, 116, 0.18);
  background: rgba(247, 215, 116, 0.055);
}

.telegramReminderPrompt.active {
  border-color: rgba(74, 222, 128, 0.20);
  background: rgba(74, 222, 128, 0.055);
}

.telegramReminderPrompt h3,
.telegramReminderPrompt p {
  margin: 0;
}

.telegramReminderPrompt h3 {
  color: rgba(255, 255, 255, 0.94);
  font-size: 1rem;
}

.telegramReminderPrompt p:not(.eyebrow) {
  margin-top: 5px;
  color: rgba(255, 255, 255, 0.70);
  line-height: 1.55;
}

.telegramConnectCode {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 10px 11px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.16);
}

.telegramConnectCode span,
.telegramConnectCode small {
  color: rgba(255, 255, 255, 0.66);
  font-size: var(--cap);
  font-weight: 780;
}

.telegramConnectCode strong {
  color: rgba(255, 255, 255, 0.94);
  letter-spacing: 0.04em;
}

.telegramPromptActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  align-items: center;
}

.telegramBotLink {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 9px 13px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 15px;
  color: rgba(219, 244, 255, 0.92);
  background: rgba(255, 255, 255, 0.055);
  font-size: 0.9rem;
  font-weight: 850;
  text-decoration: none;
}

.telegramPromptError {
  padding: 9px 10px;
  border: 1px solid rgba(248, 113, 113, 0.24);
  border-radius: 12px;
  color: rgba(254, 202, 202, 0.95);
  background: rgba(248, 113, 113, 0.08);
  font-weight: 760;
}

.missionListHead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--s-16);
}

.missionListHead h2,
.missionListHead p {
  margin: 0;
}

.missionListHead>span {
  color: var(--muted2);
  font-size: var(--cap);
}

.otherMissionContext {
  margin-top: 6px;
  max-width: 620px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.5;
}

.otherMissionHint {
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.55;
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.missionItems {
  display: grid;
  gap: var(--s-12);
}

.missionTimeline {
  display: grid;
  gap: var(--s-14);
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.018)),
    rgba(5, 10, 18, 0.18);
}

.plannerCallout {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  gap: var(--s-12);
  padding: 12px;
  border: 1px solid rgba(110, 229, 255, 0.14);
  border-radius: 16px;
  background: rgba(110, 229, 255, 0.055);
}

.plannerCallout p {
  margin: 0;
  color: rgba(219, 244, 255, 0.82);
  font-size: var(--body);
  line-height: 1.45;
}

.timelineStage {
  display: grid;
  grid-template-columns: minmax(260px, 28%) minmax(0, 1fr);
  gap: var(--s-16);
  align-items: stretch;
}

.timelineColumn {
  display: grid;
  align-content: start;
  gap: var(--s-12);
  min-width: 0;
}

.timelineRail {
  position: relative;
  width: 100%;
  max-width: 360px;
  height: clamp(520px, 72vh, 760px);
  min-height: 520px;
  margin-inline: auto;
  padding-block: 34px;
  padding-inline: 12px 112px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  background:
    radial-gradient(circle at 44px 12%, rgba(167, 139, 250, 0.10), transparent 32%),
    rgba(2, 6, 14, 0.28);
  overflow: hidden;
}

.timelineRail.compact {
  height: clamp(460px, 62vh, 640px);
  min-height: 460px;
}

.timelineRail::before {
  content: "";
  position: absolute;
  inset-block: 34px;
  inset-inline-start: 63px;
  width: 3px;
  border-radius: 999px;
  background: linear-gradient(180deg,
      rgba(167, 139, 250, 0.48),
      rgba(110, 229, 255, 0.22),
      rgba(247, 215, 116, 0.34));
  box-shadow: 0 0 22px rgba(110, 229, 255, 0.08);
}

.timelineResetLabels {
  position: absolute;
  inset-block: 14px;
  inset-inline-end: 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 104px;
  color: rgba(255, 255, 255, 0.48);
  font-size: var(--cap);
  font-weight: 820;
  line-height: 1.35;
  text-align: end;
}

.timelineTrack {
  position: absolute;
  inset-block: 34px;
  inset-inline: 0 15px;
}

.timelineGuide {
  position: absolute;
  inset-inline: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  direction: ltr;
  transform: translateY(-50%);
  pointer-events: none;
}

.timelineGuideLine {
  flex: 1;
  height: 1px;
  margin-inline-start: 74px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.10), rgba(255, 255, 255, 0.025));
}

.timelineGuideLabel {
  width: 76px;
  color: rgba(255, 255, 255, 0.38);
  font-size: var(--cap);
  font-weight: 820;
  text-align: end;
}

.timelineNow {
  position: absolute;
  inset-inline: -10px 0;
  z-index: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  direction: ltr;
  transform: translateY(-50%);
  pointer-events: none;
}

.timelineNow::before {
  content: "";
  flex: 1;
  margin-inline-start: 74px;
  height: 1px;
  background: rgba(133, 147, 150, 0.7);
}

.timelineNow span {
  width: auto;
  margin-inline-start: 0;
  margin-inline-end: -8px;
  padding: 3px 7px;
  border: 1px solid rgba(110, 229, 255, 0.24);
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.94);
  background: rgba(5, 10, 18, 0.80);
  font-size: var(--cap);
  font-weight: 900;
  text-align: end;
  white-space: nowrap;
}

.timelineCluster {
  position: absolute;
  inset-inline-start: 47px;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  direction: ltr;
  transform: translateY(-50%);
  white-space: nowrap;
}

.timelineCluster.multi {
  padding-inline-start: 40px;
}

.timelineClusterTypes {
  position: absolute;
  inset-inline-start: 0;
  top: 50%;
  z-index: 2;
  display: block;
  width: 34px;
  height: 34px;
  transform: translateY(-50%);
  pointer-events: none;
}

.timelineMarkerButton {
  --type-color: rgba(167, 139, 250, 0.96);
  --ring-color: rgba(110, 229, 255, 0.95);
  position: relative;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  padding: 0;
  border: 3px solid var(--ring-color);
  border-radius: 999px;
  background: rgba(5, 10, 18, 0.90);
  box-shadow: 0 0 0 4px rgba(5, 10, 18, 0.74), 0 12px 26px rgba(0, 0, 0, 0.28);
  cursor: pointer;
}

.timelineMarkerButton.type-main {
  --type-color: rgba(167, 139, 250, 0.98);
}

.timelineMarkerButton.type-tiny {
  --type-color: rgba(217, 70, 239, 0.96);
  border-radius: 10px;
}

.timelineMarkerButton.type-bonus {
  --type-color: rgba(247, 215, 116, 0.98);
}

.timelineMarkerButton.type-mixed {
  --type-color: conic-gradient(rgba(167, 139, 250, 0.98),
      rgba(247, 215, 116, 0.98),
      rgba(217, 70, 239, 0.96),
      rgba(167, 139, 250, 0.98));
}

.timelineMarkerButton.status-pending {
  --ring-color: rgba(110, 229, 255, 0.95);
}

.timelineMarkerButton.status-done {
  --ring-color: rgba(74, 222, 128, 0.96);
  box-shadow: 0 0 0 4px rgba(5, 10, 18, 0.74), 0 0 20px rgba(74, 222, 128, 0.16);
}

.timelineMarkerButton.status-remind_later {
  --ring-color: rgba(247, 215, 116, 0.98);
  box-shadow: 0 0 0 4px rgba(5, 10, 18, 0.74), 0 0 20px rgba(247, 215, 116, 0.14);
}

.timelineMarkerButton.status-skipped {
  --ring-color: rgba(148, 163, 184, 0.82);
  opacity: 0.84;
}

.timelineMarkerButton.status-mixed {
  --ring-color: rgba(226, 232, 240, 0.90);
}

.timelineMarkerButton.nearReset {
  --ring-color: rgba(248, 113, 113, 0.98);
  box-shadow: 0 0 0 4px rgba(5, 10, 18, 0.74), 0 0 22px rgba(248, 113, 113, 0.18);
}

.timelineMarkerButton.active {
  transform: scale(1.08);
  box-shadow: 0 0 0 4px rgba(5, 10, 18, 0.74), 0 0 0 7px rgba(110, 229, 255, 0.12), 0 16px 32px rgba(0, 0, 0, 0.30);
}

.timelineMarkerShape {
  position: relative;
  display: grid;
  place-items: center;
  width: 14px;
  height: 14px;
  border-radius: 999px;
  background: var(--type-color);
}

.timelineMarkerButton.type-tiny .timelineMarkerShape {
  border-radius: 4px;
}

.timelineMarkerButton.type-bonus .timelineMarkerShape {
  width: 17px;
  height: 17px;
  border-radius: 0;
  clip-path: polygon(50% 0, 62% 34%, 98% 35%, 69% 56%, 80% 92%, 50% 70%, 20% 92%, 31% 56%, 2% 35%, 38% 34%);
}

.timelineMarkerButton.type-mixed .timelineMarkerShape {
  border-radius: 999px;
}

.timelineMarkerCount {
  color: rgba(5, 10, 18, 0.94);
  font-size: 0.58rem;
  font-weight: 950;
  line-height: 1;
}

.timelineMarkerXp {
  padding: 7px 8px 0px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.88);
  background: rgba(110, 229, 255, 0.07);
  font-size: var(--cl-16);
  font-weight: 900;
  white-space: nowrap;
}

.timelineMarkerXp.earned {
  border-color: rgba(74, 222, 128, 0.22);
  color: rgba(187, 247, 208, 0.92);
  background: rgba(74, 222, 128, 0.07);
}

.timelineMarkerXp.reminder {
  border-color: rgba(247, 215, 116, 0.24);
  color: rgba(253, 230, 138, 0.92);
  background: rgba(247, 215, 116, 0.07);
}

.timelineMarkerXp.inactive {
  border-color: rgba(148, 163, 184, 0.18);
  color: rgba(203, 213, 225, 0.72);
  background: rgba(148, 163, 184, 0.055);
}

.timelineMarkerXp.danger,
.timelineMarkerXp.nearReset {
  border-color: rgba(248, 113, 113, 0.24);
  color: rgba(254, 202, 202, 0.92);
  background: rgba(248, 113, 113, 0.07);
}

.timelineUntimedItem.active {
  border-color: rgba(110, 229, 255, 0.32);
  box-shadow: 0 0 0 1px rgba(110, 229, 255, 0.07);
}

.timelineUntimedItem span,
.timelineUntimedItem small {
  color: rgba(255, 255, 255, 0.58);
  font-size: var(--cap);
  font-weight: 820;
}

.timelineUntimed {
  display: grid;
  gap: var(--s-10);
  padding-top: 2px;
}

.timelineUntimed p {
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  font-size: var(--cap);
  font-weight: 850;
}

.timelineUntimedItems {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
  margin-bottom: 15px;
}

.timelineUntimedItem {
  display: inline-grid;
  grid-template-columns: auto minmax(0, 1fr) repeat(3, auto);
  gap: 10px;
  align-items: center;
  min-width: 0;
  max-width: min(100%, 320px);
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
  text-align: left;
  cursor: pointer;
}

.timelineUntimedItem.pending {
  border-color: rgba(110, 229, 255, 0.24);
  background: rgba(110, 229, 255, 0.055);
  box-shadow: inset 0 0 0 1px rgba(110, 229, 255, 0.025);
}

.timelineUntimedItem.pending:hover {
  border-color: rgba(110, 229, 255, 0.34);
  background: rgba(110, 229, 255, 0.075);
}

.timelineUntimedItem.done {
  border-color: rgba(74, 222, 128, 0.20);
}

.timelineUntimedItem.remind_later,
.timelineUntimedItem.bonus {
  border-color: rgba(247, 215, 116, 0.22);
}

.timelineUntimedItem strong {
  min-width: 0;
  overflow: hidden;
  color: rgba(255, 255, 255, 0.91);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.timelineSupport {
  display: grid;
  gap: var(--s-10);
  align-items: start;
  padding: 2px 2px 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 15px;
}

.timelineSupport h2,
.timelineSupport p {
  margin: 0;
}

.timelineSupport h2 {
  color: rgba(255, 255, 255, 0.92);
  font-size: 1.05rem;
}

.timelineLegend {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 6px;
  margin-top: 15px;
  margin-bottom: 15px;
}

.timelineSupportActions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--s-8);
}

.timelineLegendItem,
.timelineLegendStatus {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 24px;
  padding: 3px 8px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.68);
  background: rgba(255, 255, 255, 0.035);
  font-size: var(--cap);
  font-weight: 840;
}

.timelineLegendItem i,
.timelineLegendStatus i {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(167, 139, 250, 0.95);
}

.timelineLegendItem.tiny i {
  border-radius: 3px;
  background: rgba(217, 70, 239, 0.95);
}

.timelineLegendItem.bonus i {
  width: 12px;
  height: 12px;
  border-radius: 0;
  clip-path: polygon(50% 0, 62% 34%, 98% 35%, 69% 56%, 80% 92%, 50% 70%, 20% 92%, 31% 56%, 2% 35%, 38% 34%);
  background: rgba(247, 215, 116, 0.95);
}

.timelineLegendStatus i {
  width: 13px;
  height: 13px;
  border: 2px solid rgba(110, 229, 255, 0.95);
  background: transparent;
}

.timelineLegendStatus.pending i {
  border-color: rgba(110, 229, 255, 0.95);
}

.timelineLegendStatus.done i {
  border-color: rgba(74, 222, 128, 0.95);
}

.timelineLegendStatus.remind_later i {
  border-color: rgba(247, 215, 116, 0.95);
}

.timelineLegendStatus.skipped i {
  border-color: rgba(148, 163, 184, 0.82);
}

.timelineSidePanel {
  display: flex;
  flex-direction: column;
  gap: var(--s-14);
  min-width: 0;
}

.timelineMissionRows {
  display: grid;
  gap: 12px;
}

.timelineMissionRow {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) repeat(4, auto);
  gap: 10px;
  align-items: center;
  width: 100%;
  padding: 11px 12px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.88);
  background: rgba(255, 255, 255, 0.04);
  text-align: start;
  cursor: pointer;
}

.timelineMissionRow.active {
  border-color: rgba(110, 229, 255, 0.34);
  background: rgba(110, 229, 255, 0.065);
  box-shadow: 0 0 0 1px rgba(110, 229, 255, 0.06);
}

.timelineMissionRow.done {
  border-color: rgba(74, 222, 128, 0.20);
}

.timelineMissionRow.remind_later {
  border-color: rgba(247, 215, 116, 0.22);
}

.timelineMissionRow.skipped {
  border-color: rgba(148, 163, 184, 0.16);
  opacity: 0.82;
}

.timelineMissionRow strong {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.timelineMissionTime {
  color: rgba(255, 255, 255, 0.55);
  font-size: var(--cap);
  font-weight: 850;
  white-space: nowrap;
}

.timelineMetaPill {
  padding: 5px 7px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.66);
  background: rgba(255, 255, 255, 0.035);
  font-size: var(--cap);
  font-weight: 850;
  white-space: nowrap;
}

.timelineMetaPill.minutes {
  border-color: rgba(110, 229, 255, 0.16);
  color: rgba(219, 244, 255, 0.78);
  background: rgba(110, 229, 255, 0.055);
}

.timelineMetaPill.easy {
  border-color: rgba(74, 222, 128, 0.16);
  color: rgba(187, 247, 208, 0.78);
  background: rgba(74, 222, 128, 0.045);
}

.timelineMetaPill.medium {
  border-color: rgba(247, 215, 116, 0.18);
  color: rgba(253, 230, 138, 0.82);
  background: rgba(247, 215, 116, 0.055);
}

.timelineMetaPill.hard {
  border-color: rgba(248, 113, 113, 0.18);
  color: rgba(254, 202, 202, 0.82);
  background: rgba(248, 113, 113, 0.05);
}

.timelineClusterDetails {
  display: grid;
  gap: var(--s-8);
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.035);
}

.timelineClusterDetails p {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  font-size: var(--cap);
  font-weight: 850;
}

.timelineClusterList {
  display: grid;
  gap: 7px;
}

.timelineClusterChoice {
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
  padding: 8px 9px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.035);
  text-align: left;
  cursor: pointer;
}

.timelineMiniMarker {
  width: 24px;
  height: 24px;
  border-width: 2px;
  box-shadow: 0 0 0 3px rgba(5, 10, 18, 0.56);
  cursor: inherit;
}

.timelineMiniMarker.type-tiny {
  border-radius: 8px;
}

.timelineMiniMarker.type-bonus {
  border-radius: 999px;
}

.timelineMiniMarker .timelineMarkerShape {
  width: 10px;
  height: 10px;
}

.timelineMiniMarker.type-bonus .timelineMarkerShape {
  width: 12px;
  height: 12px;
  border-radius: 0;
  clip-path: polygon(50% 0, 62% 34%, 98% 35%, 69% 56%, 80% 92%, 50% 70%, 20% 92%, 31% 56%, 2% 35%, 38% 34%);
}

.timelineClusterMiniMarker {
  position: absolute;
  width: 18px;
  height: 18px;
  border-width: 2px;
  box-shadow: 0 0 0 2px rgba(5, 10, 18, 0.56);
  pointer-events: none;
}

.timelineClusterMiniMarker:nth-child(1) {
  inset-inline-start: 0;
  top: 0;
}

.timelineClusterMiniMarker:nth-child(2) {
  inset-inline-start: 15px;
  top: 0;
}

.timelineClusterMiniMarker:nth-child(3) {
  inset-inline-start: 0;
  bottom: 0;
}

.timelineClusterMiniMarker:nth-child(4) {
  inset-inline-start: 15px;
  bottom: 0;
}

.timelineClusterMiniMarker:nth-child(n + 5) {
  inset-inline-start: 7px;
  top: 8px;
}

.timelineClusterMiniMarker.type-tiny {
  border-radius: 6px;
}

.timelineClusterMiniMarker.type-bonus {
  border-radius: 999px;
}

.timelineClusterMiniMarker .timelineMarkerShape {
  width: 7px;
  height: 7px;
}

.timelineClusterMiniMarker.type-bonus .timelineMarkerShape {
  width: 9px;
  height: 9px;
  border-radius: 0;
  clip-path: polygon(50% 0, 62% 34%, 98% 35%, 69% 56%, 80% 92%, 50% 70%, 20% 92%, 31% 56%, 2% 35%, 38% 34%);
}

.timelineClusterChoice.active {
  border-color: rgba(110, 229, 255, 0.30);
  background: rgba(110, 229, 255, 0.07);
}

.timelineClusterChoice span,
.timelineClusterChoice small {
  color: rgba(255, 255, 255, 0.56);
  font-size: var(--cap);
  font-weight: 820;
  white-space: nowrap;
}

.timelineClusterChoice strong {
  min-width: 0;
  overflow: hidden;
  color: rgba(255, 255, 255, 0.90);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.timelineDetail {
  margin-top: 0;
  margin-bottom: 4px;
}

.timelineDetailPlaceholder {
  display: grid;
  align-content: center;
  min-height: 100px;
  padding: 18px;
  border: 1px dashed rgba(255, 255, 255, 0.13);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.035);
}

.timelineDetailPlaceholder h3,
.timelineDetailPlaceholder p {
  margin: 0;
}

.timelineDetailPlaceholder h3 {
  color: rgba(255, 255, 255, 0.90);
  font-size: 1.05rem;
}

.timelineDetailPlaceholder p:not(.eyebrow) {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.55;
}

.timelineSidePanel .missionItem {
  grid-template-columns: 1fr;
  align-content: start;
}

.timelineSidePanel .missionActions {
  justify-content: flex-start;
}

.timelineDetailHero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: var(--s-12);
  align-items: start;
}

.timelineDetailMarker {
  cursor: default;
  pointer-events: none;
}

.missionChip.xp {
  border-color: rgba(110, 229, 255, 0.18);
  color: rgba(219, 244, 255, 0.90);
  background: rgba(110, 229, 255, 0.07);
}

.missionChip.xp.earned {
  border-color: rgba(74, 222, 128, 0.22);
  color: rgba(187, 247, 208, 0.94);
  background: rgba(74, 222, 128, 0.075);
}

.missionChip.xp.reminder {
  border-color: rgba(247, 215, 116, 0.24);
  color: rgba(253, 230, 138, 0.94);
  background: rgba(247, 215, 116, 0.075);
}

.missionChip.xp.inactive {
  border-color: rgba(148, 163, 184, 0.18);
  color: rgba(203, 213, 225, 0.74);
  background: rgba(148, 163, 184, 0.055);
}

.missionChip.xp.danger {
  border-color: rgba(248, 113, 113, 0.24);
  color: rgba(254, 202, 202, 0.92);
  background: rgba(248, 113, 113, 0.07);
}

.missionChip.minutes {
  border-color: rgba(110, 229, 255, 0.16);
  color: rgba(219, 244, 255, 0.84);
  background: rgba(110, 229, 255, 0.055);
}

.missionChip.difficulty.easy {
  border-color: rgba(74, 222, 128, 0.15);
  color: rgba(187, 247, 208, 0.82);
  background: rgba(74, 222, 128, 0.045);
}

.missionChip.difficulty.medium {
  border-color: rgba(247, 215, 116, 0.18);
  color: rgba(253, 230, 138, 0.84);
  background: rgba(247, 215, 116, 0.055);
}

.missionChip.difficulty.hard {
  border-color: rgba(248, 113, 113, 0.18);
  color: rgba(254, 202, 202, 0.84);
  background: rgba(248, 113, 113, 0.05);
}

.collapsedMissionStatus {
  align-items: center;
}

.missionItem {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: center;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.035);
}

.missionItem.done {
  border-color: rgba(74, 222, 128, 0.24);
  background: rgba(74, 222, 128, 0.06);
}

.missionItem.focus {
  border-color: rgba(247, 215, 116, 0.28);
  box-shadow: 0 0 0 1px rgba(247, 215, 116, 0.05), 0 18px 45px rgba(0, 0, 0, 0.16);
}

.missionItem.optionalNext {
  border-color: rgba(247, 215, 116, 0.24);
}

.missionItem.remind_later {
  border-color: rgba(247, 215, 116, 0.24);
  background: rgba(247, 215, 116, 0.055);
}

.missionItem.skipped {
  opacity: 0.68;
}

.missionItem h3,
.missionItem p {
  margin: 0;
}

.missionItem h3 {
  margin-top: 4px;
}

.missionChips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  margin-bottom: 6px;
}

.missionChip {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.045);
  font-size: var(--cap);
  font-weight: 850;
  line-height: 1.2;
}

.missionChip.main,
.missionChip.pending {
  border-color: rgba(110, 229, 255, 0.18);
  color: rgba(219, 244, 255, 0.92);
  background: rgba(110, 229, 255, 0.07);
}

.missionChip.tiny,
.missionChip.done {
  border-color: rgba(74, 222, 128, 0.22);
  color: rgba(187, 247, 208, 0.94);
  background: rgba(74, 222, 128, 0.07);
}

.missionChip.bonus,
.missionChip.remind_later {
  border-color: rgba(247, 215, 116, 0.24);
  color: rgba(253, 230, 138, 0.94);
  background: rgba(247, 215, 116, 0.07);
}

.missionChip.skipped {
  color: rgba(255, 255, 255, 0.68);
  background: rgba(255, 255, 255, 0.04);
}

.missionItem p:not(.missionMeta) {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.missionRelationCopy {
  display: block;
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.50);
  font-size: var(--cap);
  font-weight: 760;
  line-height: 1.4;
}

.missionMeta {
  color: rgba(110, 229, 255, 0.78);
  font-size: var(--cap);
  font-weight: 850;
}

.missionActions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--s-8);
}

.primaryMissionActions {
  justify-content: flex-start;
  margin-top: 4px;
}

.missionActionEducation {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-top: var(--s-12);
}

.educationItem {
  display: grid;
  gap: 4px;
  padding: 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.educationItem strong {
  color: rgba(255, 255, 255, 0.88);
  font-size: 0.76rem;
  font-weight: 820;
}

.educationItem span {
  color: rgba(255, 255, 255, 0.56);
  font-size: 0.72rem;
  line-height: 1.45;
}

.firstRunMissionIntro {
  display: grid;
  gap: 6px;
  padding: 14px;
  margin-bottom: var(--s-12);
  border-radius: 18px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.10), transparent 34%),
    rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(110, 229, 255, 0.14);
}

.firstRunMissionIntro h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.05rem;
  line-height: 1.35;
}

.firstRunMissionIntro p {
  margin: 0;
}

.firstRunMissionIntro p:not(.eyebrow) {
  color: rgba(255, 255, 255, 0.64);
  line-height: 1.65;
}

@media (max-width: 760px) {
  .restModeCard {
    grid-template-columns: 1fr;
    min-height: 0;
    padding: 20px;
  }

  .restModeSprite {
    width: min(160px, 55vw);
  }

  .restModeActions {
    grid-column: auto;
  }

  .restModeActions :deep(.btn),
  .missionStatusToggle :deep(.btn) {
    width: 100%;
  }

  .missionStepper {
    grid-template-columns: 1fr;
  }

  .timelineStage {
    grid-template-columns: 1fr;
    gap: var(--s-14);
  }

  .plannerCallout {
    display: grid;
  }

  .plannerCallout :deep(.btn) {
    width: 100%;
  }

  .timelineRail {
    max-width: none;
    height: min(78vh, 720px);
    min-height: 520px;
    padding-block: 34px;
    padding-inline: 10px 86px;
  }

  .timelineRail.compact {
    height: min(72vh, 640px);
    min-height: 460px;
  }

  .timelineRail::before {
    inset-inline-start: 45px;
  }

  .timelineResetLabels {
    width: 72px;
  }

  .timelineNow::before {
    margin-inline-start: 56px;
  }

  .timelineCluster {
    inset-inline-start: 31px;
  }

  .timelineGuideLine {
    margin-inline-start: 56px;
  }

  .timelineGuideLabel {
    width: 60px;
  }

  .timelineSupport {
    grid-template-columns: 1fr;

  }

  .timelineLegend {
    justify-content: flex-start;
  }

  .timelineSupportActions {
    justify-content: stretch;
  }

  .timelineSupportActions :deep(.btn) {
    flex: 1 1 100%;
  }

  .timelineClusterChoice {
    grid-template-columns: auto auto minmax(0, 1fr);
  }

  .timelineClusterChoice small {
    grid-column: 3;
  }

  .timelineUntimedItems {
    display: grid;
  }

  .timelineUntimedItem {
    max-width: 100%;
  }

  .timelineMissionRows {
    gap: 12px;
  }

  .missionGuideActions :deep(.btn),
  .remindOptions :deep(.btn),
  .customReminderControls :deep(.btn),
  .customReminderControls input,
  .skipReasons :deep(.btn),
  .completedChoices :deep(.btn),
  .optionalNextActions :deep(.btn),
  .primaryMissionActions :deep(.btn),
  .missionListHead :deep(.btn),
  .missionGuideLink,
  .completedChoices .missionGuideLink {
    width: 100%;
  }

  .missionListHead {
    display: grid;
  }

  .missionItem {
    grid-template-columns: 1fr;
  }

  .missionActions {
    justify-content: stretch;
  }

  .missionActions :deep(.btn) {
    flex: 1 1 100%;
  }

  .missionActionEducation {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .firstRunRevealPanel .firstRunRevealStep {
    opacity: 1;
    transform: none;
    animation: none;
  }
}

:global([dir="rtl"]) .timelineSupport,
:global([dir="rtl"]) .timelineClusterChoice,
:global([dir="rtl"]) .timelineUntimedItem,
:global([dir="rtl"]) .timelineMissionRow,
:global([dir="rtl"]) .timelineDetailPlaceholder,
:global([dir="rtl"]) .timelineSidePanel .missionItem {
  text-align: right;
}

:global([dir="rtl"]) .timelineUntimedItems {
  direction: rtl;
}

:global([dir="rtl"]) .timelineLegend,
:global([dir="rtl"]) .timelineSidePanel .missionActions {
  justify-content: flex-start;
}
</style>
