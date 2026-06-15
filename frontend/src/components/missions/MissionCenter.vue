<template>
  <section class="missionCenter">
    <RingoRewardSequence :steps="rewardSequenceSteps" :sprite="rewardSequenceSprite" @finish="finishRewardSequence" />

    <BaseCard v-if="coachActionPanel" class="coachActionPanel" :class="{ complete: !!todaySavedLabel }">
      <RingoCoach v-if="showCoach" embedded :message="coachMessage" :sprite="coachSprite"
        :primary-action="coachPrimaryAction" :secondary-action="coachSecondaryAction" @action="handleCoachAction" />

      <div v-if="showFocusMissionCard" :id="`mission-${focusMission.mission_id}`"
        class="focusMission coachFocusMission">
        <span>{{ t("missions.ringoSuggestedMission") }}</span>
        <div v-if="focusMissionIntensity" class="missionIntensity" :class="focusMissionIntensity.intensity">
          <span>{{ focusMissionIntensity.label }}</span>
          <small v-if="focusMissionIntensity.detail">{{ focusMissionIntensity.detail }}</small>
        </div>
        <strong>{{ focusMission.title }}</strong>
        <p>{{ focusMission.description }}</p>
        <small v-if="missionStatusCopy(focusMission)" class="missionStatusCopy">
          {{ missionStatusCopy(focusMission) }}
        </small>
        <div v-if="showFocusMissionActions" class="missionActions primaryMissionActions">
          <BaseButton variant="primary" :loading="busyId === focusMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(focusMission, 'done')" @click="markDone(focusMission)">
            {{ t("missions.doneCta") }}
          </BaseButton>

          <BaseButton variant="secondary" :loading="busyId === focusMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(focusMission, 'done')" @click="remindLater(focusMission)">
            {{ missionHasStatus(focusMission, "remind_later") ? t("missions.editReminder") : t("missions.remindLater")
            }}
          </BaseButton>

          <BaseButton v-if="shouldShowFocusSupportAction('make_smaller', focusMission)" variant="secondary"
            @click="handleFocusSupportAction('make_smaller', focusMission)">
            {{ t("missions.ringoActions.make_smaller") }}
          </BaseButton>

          <BaseButton v-if="shouldShowFocusSupportAction('too_tired', focusMission)" variant="secondary"
            @click="handleFocusSupportAction('too_tired', focusMission)">
            {{ t("missions.ringoActions.too_tired") }}
          </BaseButton>

          <BaseButton v-if="shouldShowFullVersionAction(focusMission)" variant="secondary"
            @click="focusMainMissionVariant(focusMission)">
            {{ t("missions.ringoActions.useFullVersion") }}
          </BaseButton>

          <BaseButton variant="secondary" :loading="busyId === focusMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(focusMission, 'done', 'skipped')" @click="skipMission(focusMission)">
            {{ missionHasStatus(focusMission, "skipped") ? t("missions.skipped") : t("missions.skip") }}
          </BaseButton>
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

      <p v-if="todaySavedLabel" class="todaySaved">
        <strong>{{ todaySavedLabel }}</strong>
        <span v-if="showTodaySavedBody">{{ t("missions.todaySavedBody") }}</span>
      </p>

      <section v-if="isTodaySaved && optionalNextMission" class="optionalNextStep">
        <div class="optionalNextCopy">
          <p class="eyebrow compact">{{ t("missions.optionalNextEyebrow") }}</p>
          <h3>{{ t("missions.optionalNextTitle") }}</h3>
          <p>{{ t("missions.optionalNextBody") }}</p>
        </div>

        <div class="optionalNextMission">
          <div v-if="optionalNextMissionIntensity" class="missionIntensity"
            :class="optionalNextMissionIntensity.intensity">
            <span>{{ optionalNextMissionIntensity.label }}</span>
            <small v-if="optionalNextMissionIntensity.detail">
              {{ optionalNextMissionIntensity.detail }}
            </small>
          </div>
          <strong>{{ optionalNextMission.title }}</strong>
          <p>{{ optionalNextMission.description }}</p>
          <small v-if="optionalNextMission.challenge_name" class="missionStatusCopy">
            {{ optionalNextMission.challenge_name }}
          </small>
        </div>

        <div class="optionalNextActions">
          <BaseButton variant="primary" :loading="busyId === optionalNextMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(optionalNextMission, 'done')" @click="markDone(optionalNextMission)">
            {{ t("missions.doneCta") }}
          </BaseButton>
          <BaseButton variant="secondary"
            :loading="busyId === optionalNextMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(optionalNextMission, 'done')"
            @click="remindOptionalNextMission(optionalNextMission)">
            {{ missionHasStatus(optionalNextMission, "remind_later") ? t("missions.editReminder") :
              t("missions.remindLater") }}
          </BaseButton>
          <BaseButton v-if="shouldShowOptionalNextSupportAction('make_smaller', optionalNextMission)"
            variant="secondary" @click="handleOptionalNextSupportAction('make_smaller', optionalNextMission)">
            {{ t("missions.ringoActions.make_smaller") }}
          </BaseButton>
          <BaseButton v-if="shouldShowOptionalNextSupportAction('too_tired', optionalNextMission)" variant="secondary"
            @click="handleOptionalNextSupportAction('too_tired', optionalNextMission)">
            {{ t("missions.ringoActions.too_tired") }}
          </BaseButton>
          <BaseButton variant="secondary" :loading="busyId === optionalNextMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(optionalNextMission, 'skipped')"
            @click="skipOptionalNextMission(optionalNextMission)">
            {{ t("missions.skip") }}
          </BaseButton>
          <BaseButton variant="secondary" @click="finishForToday">
            {{ t("missions.finishForToday") }}
          </BaseButton>
        </div>
      </section>

      <div v-if="isTodaySaved" class="completedChoices">
        <RouterLink v-if="detailsMission?.enrollment_id" class="missionGuideLink"
          :to="`/enrollment/${detailsMission.enrollment_id}`">
          {{ t("missions.detailsCta") }}
        </RouterLink>

        <BaseButton v-if="otherMissions.length && !optionalNextSuppressed && !showOtherMissions" variant="secondary"
          @click="showOtherMissions = true">
          {{ t("missions.showOtherMissions", { count: otherMissions.length }) }}
        </BaseButton>

        <BaseButton v-if="!optionalNextMission" variant="secondary" @click="finishForToday">
          {{ t("missions.finishForToday") }}
        </BaseButton>
      </div>

    </BaseCard>

    <UiState :loading="loading" :error="!!error" :empty="false" :loading-title="t('missions.loadingTitle')"
      :loading-text="t('missions.loadingText')" :error-title="t('missions.errorTitle')"
      :error-text="error || t('common.pleaseTryAgain')" @retry="loadMissions" />

    <p v-if="showMissionNotice" class="missionNotice" :class="noticeType">
      {{ notice }}
    </p>

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
        <span>{{ guidanceMission ? t("missions.ringoSuggestedMission") : t("missions.nextMission") }}</span>
        <div v-if="focusMissionIntensity" class="missionIntensity" :class="focusMissionIntensity.intensity">
          <span>{{ focusMissionIntensity.label }}</span>
          <small v-if="focusMissionIntensity.detail">{{ focusMissionIntensity.detail }}</small>
        </div>
        <strong>{{ focusMission.title }}</strong>
        <p>{{ focusMission.description }}</p>
        <small v-if="missionStatusCopy(focusMission)" class="missionStatusCopy">
          {{ missionStatusCopy(focusMission) }}
        </small>
        <div v-if="showFocusMissionActions" class="missionActions primaryMissionActions">
          <BaseButton variant="primary" :loading="busyId === focusMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(focusMission, 'done')" @click="markDone(focusMission)">
            {{ t("missions.doneCta") }}
          </BaseButton>

          <BaseButton variant="secondary" :loading="busyId === focusMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(focusMission, 'done')" @click="remindLater(focusMission)">
            {{ missionHasStatus(focusMission, "remind_later") ? t("missions.editReminder") : t("missions.remindLater")
            }}
          </BaseButton>

          <BaseButton v-if="shouldShowFocusSupportAction('make_smaller', focusMission)" variant="secondary"
            @click="handleFocusSupportAction('make_smaller', focusMission)">
            {{ t("missions.ringoActions.make_smaller") }}
          </BaseButton>

          <BaseButton v-if="shouldShowFocusSupportAction('too_tired', focusMission)" variant="secondary"
            @click="handleFocusSupportAction('too_tired', focusMission)">
            {{ t("missions.ringoActions.too_tired") }}
          </BaseButton>

          <BaseButton v-if="shouldShowFullVersionAction(focusMission)" variant="secondary"
            @click="focusMainMissionVariant(focusMission)">
            {{ t("missions.ringoActions.useFullVersion") }}
          </BaseButton>

          <BaseButton variant="secondary" :loading="busyId === focusMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(focusMission, 'done', 'skipped')" @click="skipMission(focusMission)">
            {{ missionHasStatus(focusMission, "skipped") ? t("missions.skipped") : t("missions.skip") }}
          </BaseButton>
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

    <BaseCard v-if="showOtherMissionList" class="missionList secondaryMissionList">
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
                  <BaseButton variant="secondary" @click="showOtherMissions = false">
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
                    </div>

                    <div v-if="showMissionItemActions(mission)" class="missionActions">
                      <BaseButton variant="primary" :loading="busyId === mission.mission_id && busyAction === 'done'"
                        :disabled="missionHasStatus(mission, 'done')" @click="markDone(mission)">
                        {{ t("missions.doneCta") }}
                      </BaseButton>

                      <BaseButton variant="secondary"
                        :loading="busyId === mission.mission_id && busyAction === 'remind'"
                        :disabled="missionHasStatus(mission, 'done')" @click="remindLater(mission)">
                        {{ missionHasStatus(mission, "remind_later") ? t("missions.editReminder") :
                          t("missions.remindLater") }}
                      </BaseButton>

                      <BaseButton variant="secondary" :loading="busyId === mission.mission_id && busyAction === 'skip'"
                        :disabled="missionHasStatus(mission, 'done', 'skipped')" @click="skipMission(mission)">
                        {{ missionHasStatus(mission, "skipped") ? t("missions.skipped") : t("missions.skip") }}
                      </BaseButton>

                      <BaseButton v-if="shouldShowMissionItemTinyAction(mission)" variant="secondary"
                        @click="focusTinyMissionVariant(mission)">
                        {{ t("missions.ringoActions.tryTinyVersion") }}
                      </BaseButton>

                      <BaseButton v-if="shouldShowFullVersionAction(mission)" variant="secondary"
                        @click="focusMainMissionVariant(mission)">
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
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";
import RingoCoach from "@/components/ringo/RingoCoach.vue";
import RingoRewardSequence from "@/components/ringo/RingoRewardSequence.vue";
import PathSelection from "@/components/missions/PathSelection.vue";
import {
  localizeMissionList,
  localizeRingoState,
} from "@/lib/ringoContentLocalization";

const { locale, t } = useI18n();
const emit = defineEmits(["checked-in", "loaded"]);

const loading = ref(true);
const error = ref("");
const date = ref("");
const ringo = ref(null);
const ringoGuidance = ref(null);
const missions = ref([]);
const busyId = ref(null);
const busyAction = ref("");
const notice = ref("");
const noticeType = ref("success");
const dismissedCoachState = ref("");
const interactionNarrative = ref(null);
const completionNarrative = ref(null);
const manualFocusMissionId = ref(null);
const showOtherMissions = ref(true);
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
const revealedTinyMissionIds = ref(new Set());

const SUPPORTED_GUIDANCE_ACTIONS = new Set([
  "start",
  "remind_later",
  "make_smaller",
  "too_tired",
  "skip_today",
]);

const SUPPORTED_REWARD_STEP_TYPES = new Set([
  "ringo_message",
  "mission_completed",
  "xp_earned",
  "today_saved",
  "next_choice",
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

const finishedForTodayNarrative = computed(() => {
  if (!optionalNextSuppressed.value || !isTodaySaved.value) return null;

  return doneForTodayAgendaNarrative();
});

const dailySummaryNarrative = computed(() => {
  if (!isTodaySaved.value || !localizedMissions.value.length) return null;

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
  return interactionNarrative.value
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

  const currentMission = localizedMissions.value.find((item) => item.mission_id === mission.mission_id);

  return currentMission ? { ...mission, ...currentMission } : mission;
});

const pendingMissions = computed(() => {
  return localizedMissions.value.filter((mission) => missionHasStatus(mission, "pending"));
});

const deferredMissions = computed(() => {
  return localizedMissions.value.filter((mission) => missionHasStatus(mission, "remind_later"));
});

const skippedMissions = computed(() => {
  return localizedMissions.value.filter((mission) => missionHasStatus(mission, "skipped"));
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
    || primaryReminderMission()
    || guidanceMission.value
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

    if (meaningfulTiny) {
      representatives.push(meaningfulTiny);
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
  const candidates = effectiveMissionRepresentatives.value.filter((mission) => {
    if (!missionHasStatus(mission, "pending")) return false;
    if (isFocusMissionRendered() && sameMissionId(mission.mission_id, focusMission.value?.mission_id)) return false;

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

  return safeOptionalMissions.value[0] || null;
});

const otherMissions = computed(() => {
  return curatedOtherMissions.value.filter(shouldShowOtherMissionItem);
});

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

const showTodaySavedBody = computed(() => {
  if (optionalNextMission.value) return true;
  if (finishedForTodayNarrative.value) return false;
  if (agendaNarrative.value?.mood === "sleeping") return false;

  return guidanceAgenda.value?.next_action_type !== "done_for_today";
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

async function loadMissions() {
  loading.value = true;
  error.value = "";
  clearNarrativeState();
  manualFocusMissionId.value = null;
  showOtherMissions.value = true;
  selectedTimelineMissionId.value = null;
  reminderPanelMissionId.value = null;
  customReminderPanelMissionId.value = null;
  customReminderTime.value = "";
  skipReasonPanelMissionId.value = null;

  try {
    const [missionsResult, guidanceResult] = await Promise.allSettled([
      api.get("/me/today-missions"),
      api.get("/me/ringo/today"),
    ]);

    if (missionsResult.status === "rejected") {
      throw missionsResult.reason;
    }

    const { data } = missionsResult.value;
    ringoGuidance.value = guidanceResult.status === "fulfilled"
      ? guidanceResult.value?.data || null
      : null;
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

async function runMissionAction(mission, action, request, options = {}) {
  busyId.value = mission.mission_id;
  busyAction.value = action;
  error.value = "";

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

    if (data?.checkin?.ok) {
      emit("checked-in", {
        ...data,
        mission: {
          ...mission,
          ...(data?.mission || {}),
          title: mission.title,
          description: mission.description,
          challenge_name: mission.challenge_name,
          path_title: mission.path_title,
        },
      });
    }

    if (action === "done") {
      rewardSequenceSteps.value = buildRewardSequence(data, mission);
      rewardSequenceSprite.value = data?.checkin?.already_checked ? "happy" : "celebration";
    }

    applyMissionResponse(data, mission);
    await loadMissions();
    if (action === "remind") {
      preferMainMissionAfterReminder(mission);
      manualFocusMissionId.value = mission.mission_id;
      selectedTimelineMissionId.value = mission.mission_id;
    }
    if (options.narrative) {
      setNarrative(options.narrative);
    } else if (action === "done") {
      completionNarrative.value = {
        message: t("missions.narrative.completed", { mission: mission.title }),
        mood: "proud",
      };
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
    manualFocusMissionId.value = mission.mission_id;
    selectedTimelineMissionId.value = mission.mission_id;
    showOtherMissions.value = true;
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
  const successNotice = reason?.key && reason.key !== "withoutReason"
    ? t("missions.skipReasons.confirmationWithReason", { reason: reason.label })
    : t("missions.skipReasons.confirmationWithoutReason");
  const requestBody = reason?.reason ? { reason: reason.reason } : {};

  return runMissionAction(
    mission,
    "skip",
    () => postMissionSkip(mission.mission_id, requestBody),
    {
      successNotice,
      narrative: {
        message: reason?.key && reason.key !== "withoutReason"
          ? t("missions.narrative.skipConfirmedWithReason", { reason: reason.label })
          : t("missions.narrative.skipConfirmedWithoutReason"),
        mood: "concerned",
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

function rewardStepFallbackTitle(type, mission) {
  const titleMap = {
    ringo_message: "ringoTitle",
    mission_completed: "missionFallback",
    xp_earned: "xpTitle",
    today_saved: "todaySavedTitle",
    next_choice: "nextTitle",
  };

  if (type === "mission_completed") {
    return mission?.title || t("ringoRewardSequence.local.missionFallback");
  }

  return t(`ringoRewardSequence.local.${titleMap[type] || "missionFallback"}`);
}

function rewardStepFallbackText(type) {
  const textMap = {
    ringo_message: "ringoText",
    mission_completed: "missionText",
    today_saved: "todaySavedText",
    next_choice: "nextText",
  };

  return textMap[type] ? t(`ringoRewardSequence.local.${textMap[type]}`) : "";
}

function rewardStepValue(step) {
  if (step?.value !== undefined && step?.value !== null && String(step.value).trim()) {
    return String(step.value);
  }

  const amount = Number(step?.amount);
  if (Number.isFinite(amount) && amount > 0) {
    return t("ringoRewardSequence.local.xpValue", { count: amount });
  }

  return "";
}

function backendRewardSequenceSteps(data, mission) {
  const sequence = data?.reward_sequence;
  if (!Array.isArray(sequence)) return [];

  return sequence
    .filter((step) => {
      return step && typeof step === "object" && SUPPORTED_REWARD_STEP_TYPES.has(step.type);
    })
    .map((step) => ({
      type: step.type,
      label: step.label ? String(step.label) : "",
      title: step.title ? String(step.title) : rewardStepFallbackTitle(step.type, mission),
      text: step.text || step.description || step.message
        ? String(step.text || step.description || step.message)
        : rewardStepFallbackText(step.type),
      value: rewardStepValue(step),
      sprite: step.mood || step.sprite_key,
    }))
    .filter((step) => step.title || step.text || step.value);
}

function buildRewardSequence(data, mission) {
  const backendSteps = backendRewardSequenceSteps(data, mission);
  if (backendSteps.length) return backendSteps;

  const completedMission = data?.mission || {};
  const xpEarned = Number(completedMission.xp_earned ?? mission.xp_reward ?? 0);
  const todaySaved = Boolean(data?.checkin?.ok);
  const steps = [
    {
      type: "ringo_message",
      title: t("ringoRewardSequence.local.ringoTitle"),
      text: data?.checkin?.already_checked
        ? t("ringoRewardSequence.local.alreadySaved")
        : t("ringoRewardSequence.local.ringoText"),
      sprite: data?.checkin?.already_checked ? "happy" : "celebration",
    },
    {
      type: "mission_completed",
      title: mission.title || completedMission.title || t("ringoRewardSequence.local.missionFallback"),
      text: t("ringoRewardSequence.local.missionText"),
    },
  ];

  if (xpEarned > 0) {
    steps.push({
      type: "xp_earned",
      title: t("ringoRewardSequence.local.xpTitle"),
      value: t("ringoRewardSequence.local.xpValue", { count: xpEarned }),
    });
  }

  if (todaySaved) {
    steps.push({
      type: "today_saved",
      title: t("ringoRewardSequence.local.todaySavedTitle"),
      text: t("ringoRewardSequence.local.todaySavedText"),
    });
  }

  steps.push({
    type: "next_choice",
    title: t("ringoRewardSequence.local.nextTitle"),
    text: t("ringoRewardSequence.local.nextText"),
  });

  return steps;
}

function finishRewardSequence() {
  rewardSequenceSteps.value = [];
  showOtherMissions.value = true;
}

function finishForToday() {
  optionalNextSuppressed.value = true;
  manualFocusMissionId.value = null;
  showOtherMissions.value = true;
  setInteractionNarrative("missions.finishedForTodayMessage", "sleeping");
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

function buildMissionIntensityMeta(mission, options = {}) {
  if (!mission) return null;

  const intensity = normalizedMissionIntensity(mission);
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

  if (intensity === "bonus" && parentMission && !missionHasStatus(parentMission, "done")) {
    return false;
  }

  return true;
}

function shouldShowOtherMissionItem(mission) {
  if (!mission?.mission_id) return false;

  return true;
}

function isFocusMissionRendered() {
  if (!focusMission.value) return false;
  if (!isTodaySaved.value) return true;
  if (missionHasStatus(focusMission.value, "done")) return false;
  if (missionHasStatus(focusMission.value, "remind_later")) return true;

  return !!(
    sameMissionId(focusMission.value.mission_id, manualFocusMissionId.value)
    || isReminderPanelOpen(focusMission.value)
    || isSkipReasonPanelOpen(focusMission.value)
  );
}

function primaryReminderMission() {
  return sortReminderMissions(
    effectiveMissionRepresentatives.value.filter((mission) => {
      return missionHasStatus(mission, "remind_later");
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

function sortReminderMissions(items) {
  return [...items].sort((a, b) => {
    const aDue = isReminderDue(a);
    const bDue = isReminderDue(b);

    if (aDue !== bDue) return aDue ? -1 : 1;

    return reminderTimestamp(a) - reminderTimestamp(b);
  });
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

  if (
    status === "pending"
    && normalizedMissionIntensity(mission) === "main"
    && hasDoneTinyChild(mission)
  ) {
    return t("missions.statusCopy.optionalUpgrade");
  }

  return mission.ringo_message || "";
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

onMounted(loadMissions);
</script>

<style scoped>
.missionCenter {
  display: grid;
  gap: var(--s-16);
}

.missionList {
  display: grid;
  gap: var(--s-16);
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
  padding: 34px 112px 34px 12px;
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
  top: 34px;
  bottom: 34px;
  left: 63px;
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
  right: 14px;
  left: auto;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 104px;
  color: rgba(255, 255, 255, 0.48);
  font-size: var(--cap);
  font-weight: 820;
  line-height: 1.35;
  text-align: right;
}

.timelineTrack {
  position: absolute;
  inset: 34px 15px 34px 0;
}

.timelineGuide {
  position: absolute;
  left: 0;
  right: 0;
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
  margin-left: 74px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.10), rgba(255, 255, 255, 0.025));
}

.timelineGuideLabel {
  width: 76px;
  color: rgba(255, 255, 255, 0.38);
  font-size: var(--cap);
  font-weight: 820;
  text-align: right;
}

.timelineNow {
  position: absolute;
  left: -10px;
  right: 0;
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
  margin-left: 74px;
  height: 1px;
  background: rgba(133, 147, 150, 0.7);
}

.timelineNow span {
  width: auto;
  margin-left: 0px;
  margin-right: -8px;
  padding: 3px 7px;
  border: 1px solid rgba(110, 229, 255, 0.24);
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.94);
  background: rgba(5, 10, 18, 0.80);
  font-size: var(--cap);
  font-weight: 900;
  text-align: right;
  white-space: nowrap;
}

.timelineCluster {
  position: absolute;
  left: 47px;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  direction: ltr;
  transform: translateY(-50%);
  white-space: nowrap;
}

.timelineCluster.multi {
  padding-left: 40px;
}

.timelineClusterTypes {
  position: absolute;
  left: 0;
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
  padding: 3px 6px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.88);
  background: rgba(110, 229, 255, 0.07);
  font-size: var(--cap);
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
  grid-template-columns: auto minmax(0, 1fr) auto;
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
  grid-template-columns: auto minmax(0, 1fr) auto auto;
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

@media (max-width: 760px) {
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
    padding: 34px 86px 34px 10px;
  }

  .timelineRail.compact {
    height: min(72vh, 640px);
    min-height: 460px;
  }

  .timelineRail::before {
    left: 45px;
  }

  .timelineResetLabels {
    width: 72px;
  }

  .timelineNow::before {
    margin-left: 56px;
  }

  .timelineCluster {
    left: 31px;
  }

  .timelineGuideLine {
    margin-left: 56px;
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
